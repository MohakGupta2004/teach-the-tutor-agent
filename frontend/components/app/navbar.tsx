"use client";
import Head from "next/head";
import { motion } from "framer-motion";

export default function Navbar() {
  const navlinks = [
    { name: "Categories", href: "/categories" },
    { name: "Instructors", href: "/instructors" },
    { name: "Agents", href: "/agent" },
    {name: "About", href: "/about"}
  ]
  return (
   <>
  <div className="relative flex items-center h-16 m-2 font-serif font-bold mx-9 border-b-2 border-gray-600">
    <div className="flex items-center gap-3">
      <motion.a
        href="/"
        aria-label="Home"
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        className="flex items-center no-underline"
        style={{ fontFamily: "'Vend Sans', sans-serif" }}
      >
        <span className="text-2xl md:text-3xl font-semibold tracking-tight text-slate-300">
          Xrella
        </span>
      </motion.a>
    </div>
    {/* Center navlinks */}
    <nav className="absolute left-1/2 transform -translate-x-1/2">
      <ul className="flex gap-6 text-white font-sans font-medium">
        {navlinks.map((link) => (
          <li key={link.href}>
            <a href={link.href} className="hover:text-gray-300">
              {link.name}
            </a>
          </li>
        ))}
      </ul>
    </nav>

    {/* Right contact button */}
    <div className="absolute right-4">
      <motion.a
        href="/contact"
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        style={{ fontFamily: "'Vend Sans', sans-serif" }}
        className="inline-flex items-center gap-3 px-5 py-2 text-lg font-medium text-slate-300 rounded-full bg-transparent shadow-none hover:bg-slate-700/10 focus:outline-none focus:ring-4 focus:ring-slate-200/40 ring-offset-2 transition-colors duration-200"
        aria-label="Contact us"
      >
        <span>Contact Us</span>
      </motion.a>
    <Head>
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      <link href="https://fonts.googleapis.com/css2?family=Vend+Sans:ital,wght@0,300..700;1,300..700&display=swap" rel="stylesheet" />
    </Head>
   </div>
  </div>
   </> 
  );
}
