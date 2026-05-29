"use client";
import { motion } from "framer-motion";

export function AnimatedBackground() {
  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
      <motion.div
        animate={{
          x: [0, 600, -600, 0],
          y: [0, -400, 400, 0],
          scale: [1, 2.5, 1],
        }}
        transition={{
          duration: 3.5,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-[10%] left-[20%] w-[50vw] h-[50vw] rounded-full bg-blue-600/30 blur-[100px]"
      />
      <motion.div
        animate={{
          x: [0, -700, 700, 0],
          y: [0, 500, -500, 0],
          scale: [1, 3, 1],
        }}
        transition={{
          duration: 4.2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-[30%] right-[10%] w-[40vw] h-[40vw] rounded-full bg-indigo-500/30 blur-[120px]"
      />
      <motion.div
        animate={{
          scale: [1, 4, 1],
          opacity: [0.1, 0.9, 0.1],
        }}
        transition={{
          duration: 2.1,
          repeat: Infinity,
          ease: "circInOut"
        }}
        className="absolute bottom-[-20%] left-[30%] w-[60vw] h-[30vw] rounded-full bg-cyan-400/20 blur-[80px]"
      />

      <motion.div 
        animate={{
          backgroundPosition: ["0px 0px", "0px 100px"]
        }}
        transition={{
          duration: 0.8,
          repeat: Infinity,
          ease: "linear"
        }}
        className="absolute inset-0 bg-[linear-gradient(rgba(0,255,255,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,255,0.1)_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_70%_70%_at_50%_50%,#000_20%,transparent_100%)]"
      />
    </div>
  );
}