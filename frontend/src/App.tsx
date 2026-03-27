"use client";

import "./App.css";
import { useState } from "react";
import { Zap, FlaskConical, BarChart3 } from "lucide-react";

import type { Attack, Defense, Model, Prompt } from "./types";
import attacks from "./components/attacks";
import defenses from "./components/defenses";
import models from "./components/models";

import AttackSelector from "./components/AttackSelector";
import DefenseSelector from "./components/DefenseSelector";
import ModelSelector from "./components/ModelSelector";
import ExecutionHistory from "./components/ExecutionHistory";
import PromptInput from "./components/PromptInput";
import InfoModal from "./components/InfoModal";
import StatisticsView from "./components/StatisticsView";

const API_URL = (
   import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");

function App() {
   const [selectedAttack, setSelectedAttack] = useState<Attack>(attacks[0]);
   const [selectedDefense, setSelectedDefense] = useState<Defense>(defenses[0]);
   const [selectedModel, setSelectedModel] = useState<Model>(models[0]);
   const [message, setMessage] = useState("");
   const [systemPrompt, setSystemPrompt] = useState("");
   const [prompts, setPrompts] = useState<Prompt[]>([]);
   const [infoModalOpen, setInfoModalOpen] = useState(false);
   const [infoTitle, setInfoTitle] = useState("");
   const [infoBody, setInfoBody] = useState("");
   const [infoRefs, setInfoRefs] = useState<string[]>([]);
   const [abortController, setAbortController] =
      useState<AbortController | null>(null);
   const [isExecuting, setIsExecuting] = useState(false);
   const [activeView, setActiveView] = useState<"tester" | "statistics">(
      "tester",
   );

   const handleCancel = () => {
      if (abortController) {
         abortController.abort();
         setAbortController(null);
         setIsExecuting(false);
      }
   };

   const handleInfoClick = (title: string, body: string, refs: string[]) => {
      setInfoTitle(title);
      setInfoBody(body);
      setInfoRefs(refs);
      setInfoModalOpen(true);
   };

   const handleSend = async () => {
      if (!message.trim()) return;

      const currentMessage = message;
      setMessage("");

      // Create new abort controller for this request
      const controller = new AbortController();
      setAbortController(controller);
      setIsExecuting(true);

      let newIndex: number;
      setPrompts((prev) => {
         newIndex = prev.length;
         return [
            ...prev,
            {
               text: currentMessage,
               timestamp: new Date().toLocaleTimeString(),
               attack: selectedAttack,
               defense: selectedDefense,
               model: selectedModel,
               scriptOutput: "",
               progress: 0,
               isBlocked: false,
               attackSuccess: false,
               gpuInfo: "",
            },
         ];
      });

      try {
         const response = await fetch(`${API_URL}/api/prompt/stream`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
               prompt: currentMessage,
               attack: selectedAttack.id,
               defense: selectedDefense.id,
               model: selectedModel.id,
               system_prompt: window.localStorage.getItem("globalSystemPrompt") || "",
               isBlocked: false,
            }),
            signal: controller.signal,
         });

         if (!response.body) {
            const text = await response.text();
            setPrompts((prev) => {
               const copy = [...prev];
               copy[newIndex] = {
                  ...copy[newIndex],
                  scriptOutput: text,
                  progress: 100,
               };
               return copy;
            });
            return;
         }

         const reader = response.body.getReader();
         const decoder = new TextDecoder();
         let done = false;
         let localAccum = "";

         let gpuCapturedForThisPrompt = false;
         let blockedPrompt = false;
         let iterationCount = 0;

         while (!done) {
            const result = await reader.read();
            done = !!result.done;
            if (result.value) {
               const text = decoder.decode(result.value, { stream: true });
               const lines = text.split("\n");

               for (const line of lines) {
                  iterationCount++;
                  console.debug(`Iteration ${iterationCount}: Processing line`);
                  console.debug(`Line content:`, line);
                  const trimmed = line.trim();
                  if (!trimmed) continue;

                  if (!blockedPrompt && trimmed.startsWith("Blocked input")) {
                     setPrompts((prev) => {
                        const copy = [...prev];
                        if (!copy[newIndex]) return prev;
                        copy[newIndex] = {
                           ...copy[newIndex],
                           isBlocked: true,
                        };
                        return copy;
                     });
                     blockedPrompt = true;
                     continue;
                  }

                  if (trimmed.startsWith("[ATTACK_SUCCESS]")) {
                     const success =
                        trimmed.replace("[ATTACK_SUCCESS]", "").trim() ===
                        "true";
                     setPrompts((prev) => {
                        const copy = [...prev];
                        if (!copy[newIndex]) return prev;
                        copy[newIndex] = {
                           ...copy[newIndex],
                           attackSuccess: success,
                        };
                        return copy;
                     });
                     continue;
                  }

                  if (
                     !gpuCapturedForThisPrompt &&
                     (trimmed.startsWith("No compatible GPU") ||
                        trimmed.startsWith("GPU name:"))
                  ) {
                     setPrompts((prev) => {
                        const copy = [...prev];
                        if (!copy[newIndex]) return prev;
                        copy[newIndex] = {
                           ...copy[newIndex],
                           gpuInfo: trimmed,
                        };
                        return copy;
                     });
                     gpuCapturedForThisPrompt = true;
                     continue;
                  }

                  if (trimmed.startsWith("[PROGRESS]")) {
                     const percent = Number.parseFloat(
                        trimmed.replace("[PROGRESS]", "").trim(),
                     );
                     if (!isNaN(percent)) {
                        setPrompts((prev) => {
                           const copy = [...prev];
                           if (!copy[newIndex]) return prev;
                           copy[newIndex] = {
                              ...copy[newIndex],
                              progress: percent,
                           };
                           return copy;
                        });
                     }
                  } else {
                     localAccum += line + "\n";
                     setPrompts((prev) => {
                        const copy = [...prev];
                        if (!copy[newIndex]) return prev;
                        copy[newIndex] = {
                           ...copy[newIndex],
                           scriptOutput: localAccum,
                        };
                        return copy;
                     });
                  }
               }
            }
         }

         setPrompts((prev) => {
            const copy = [...prev];
            if (!copy[newIndex]) return prev;
            copy[newIndex] = { ...copy[newIndex], progress: 100 };
            return copy;
         });
      } catch (err) {
         // Check if it was cancelled (AbortError is expected when user clicks cancel)
         if (err instanceof Error && err.name === "AbortError") {
            // Don't log AbortError - it's expected when canceling
            setPrompts((prev) => {
               const copy = [...prev];
               if (!copy[newIndex]) return prev;
               copy[newIndex] = {
                  ...copy[newIndex],
                  scriptOutput: `Manually canceled`,
                  progress: 0,
               };
               return copy;
            });
         } else {
            // Log unexpected errors
            console.error("Streaming error:", err);
            setPrompts((prev) => {
               const copy = [...prev];
               if (!copy[newIndex]) return prev;
               copy[newIndex] = {
                  ...copy[newIndex],
                  scriptOutput: `Error: ${String(err)}`,
                  progress: 0,
               };
               return copy;
            });
         }
      } finally {
         setIsExecuting(false);
         setAbortController(null);
      }
   };

   return (
      <div className="min-h-screen w-full bg-gradient-to-br from-[#0a0a0f] via-[#0f0f1a] to-[#0a0a0f] p-3 md:p-4">
         <div className="max-w-[1800px] mx-auto">
            <header className="mb-4 relative">
               {/* Navigation Toggle - Top Right */}
               <div className="absolute right-0 top-0 flex gap-1">
                  <button
                     onClick={() => setActiveView("tester")}
                     className={`p-2.5 rounded-lg border transition-all duration-200 ${
                        activeView === "tester"
                           ? "bg-[#6366f1]/20 border-[#6366f1] text-[#6366f1]"
                           : "bg-[#1a1a24]/80 border-[#2d2d3d] text-[#94a3b8] hover:border-[#6366f1]/50 hover:text-[#6366f1]"
                     }`}
                     title="Tester"
                  >
                     <FlaskConical className="w-5 h-5" />
                  </button>
                  <button
                     onClick={() => setActiveView("statistics")}
                     className={`p-2.5 rounded-lg border transition-all duration-200 ${
                        activeView === "statistics"
                           ? "bg-[#6366f1]/20 border-[#6366f1] text-[#6366f1]"
                           : "bg-[#1a1a24]/80 border-[#2d2d3d] text-[#94a3b8] hover:border-[#6366f1]/50 hover:text-[#6366f1]"
                     }`}
                     title="Statistics"
                  >
                     <BarChart3 className="w-5 h-5" />
                  </button>
               </div>

               <div className="text-center">
                  <div className="flex items-center justify-center gap-2 mb-2">
                     <Zap className="text-[#6366f1] w-7 h-7" />
                     <h1 className="text-2xl lg:text-3xl font-bold bg-gradient-to-r from-[#f8fafc] to-[#cbd5e1] bg-clip-text text-transparent">
                        JailbreakLab
                     </h1>
                  </div>
                  <p className="text-[#94a3b8] text-sm max-w-2xl mx-auto leading-relaxed">
                     {activeView === "tester"
                        ? "Test AI model vulnerabilities with various attack and defense mechanisms"
                        : "View statistics and analysis of attack and defense effectiveness"}
                  </p>
               </div>
            </header>

            {activeView === "tester" ? (
               <div className="grid grid-cols-1 lg:grid-cols-[1fr_2fr] gap-3 lg:gap-4">
                  <div className="flex flex-col gap-3 h-[calc(100vh-150px)] overflow-y-auto">
                     <AttackSelector
                        selectedAttack={selectedAttack}
                        setSelectedAttack={setSelectedAttack}
                        onInfoClick={handleInfoClick}
                     />
                     <DefenseSelector
                        selectedDefense={selectedDefense}
                        setSelectedDefense={setSelectedDefense}
                        onInfoClick={handleInfoClick}
                     />
                     <ModelSelector
                        selectedModel={selectedModel}
                        setSelectedModel={setSelectedModel}
                     />
                  </div>

                  <div className="flex flex-col gap-3 h-[calc(100vh-150px)]">
                     <ExecutionHistory
                        prompts={prompts}
                        isExecuting={isExecuting}
                        onCancel={handleCancel}
                     />
                     <PromptInput
                        message={message}
                        setMessage={setMessage}
                        systemPrompt={systemPrompt}
                        setSystemPrompt={setSystemPrompt}
                        isExecuting={isExecuting}
                        onSend={handleSend}
                     />
                  </div>
               </div>
            ) : (
               <div className="h-[calc(100vh-150px)]">
                  <StatisticsView />
               </div>
            )}
         </div>

         <InfoModal
            isOpen={infoModalOpen}
            onClose={() => setInfoModalOpen(false)}
            title={infoTitle}
            body={infoBody}
            references={infoRefs}
         />
      </div>
   );
}

export default App;
