"use client";
import { motion } from "framer-motion";
import Image from "next/image";

interface HeroProps {
  onStartCall?: () => void;
}

export default function Hero({ onStartCall }: HeroProps) {
  return (
    <div className="w-full my-10 bg-black text-white flex items-center justify-center px-8 py-12">
      <div className="max-w-7xl w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* Left Content */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="space-y-8"
        >
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold leading-tight">
            Learning Made<br />
            Simple, Success<br />
            Made <span className="text-red-500">Possible</span>
          </h1>
          
          <p className="text-gray-400 text-lg max-w-md pb-5 border-b-2">
            Discover a way to teach test and teach back with the agentic
            workflows.
          </p>
          
          <button
            onClick={onStartCall}
            className="bg-white text-black px-8 py-4 rounded-full font-semibold text-lg hover:bg-gray-200 transition-all duration-300 inline-block"
          >
            Explore now
          </button>
        </motion.div>

        {/* Right Image Section */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="relative flex justify-center lg:justify-end"
        >
          {/* Purple rounded rectangle background */}
          <div className="relative">
            <div className="absolute inset-0 bg-purple-400 rounded-[2.5rem] transform translate-x-4 translate-y-4" />
            
            {/* Badge */}
            <div className="absolute top-8 left-8 bg-purple-300 text-purple-900 px-4 py-2 rounded-2xl font-semibold text-sm z-20">
              #1 Learning<br />Platform with<br />AI agents
            </div>
            
            {/* Image container */}
            <div className="relative bg-purple-300 rounded-[2.5rem] overflow-hidden w-[400px] h-[500px] lg:w-[450px] lg:h-[550px]">
              <Image
                src="/teacher.jpg"
                alt="Learning Platform"
                fill
                className="object-cover"
                priority
              />
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
