import * as React from "react"

import { cn } from "@/utils"

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "flex items-center field-sizing-content min-h-16 w-full rounded-lg border-2 border-white/30 bg-white/10 backdrop-blur-md px-4 py-3 text-base text-gray-800 placeholder:text-gray-500 shadow-lg transition-all duration-300 outline-none focus:border-purple-400 focus:bg-white/20 focus:ring-2 focus:ring-purple-500/30 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm hover:border-white/40 leading-normal",
        className
      )}
      {...props}
    />
  )
}

export { Textarea }
