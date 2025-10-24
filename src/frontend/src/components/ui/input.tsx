import * as React from "react"

import { cn } from "@/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "flex h-9 w-full min-w-0 rounded-lg border-2 border-white/30 bg-white/10 backdrop-blur-md px-4 py-2 text-base text-gray-800 placeholder:text-gray-500 shadow-lg transition-all duration-300 outline-none",
        "focus:border-purple-400 focus:bg-white/20 focus:ring-2 focus:ring-purple-500/30",
        "file:text-gray-800 file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium",
        "disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50",
        "hover:border-white/40",
        "md:text-sm",
        className
      )}
      {...props}
    />
  )
}

export { Input }
