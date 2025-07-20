/* This is a button component for redirect when user clicks */

"use client"
import { useState } from "react";
import { useRouter } from "next/navigation";

export type MyButtonProps = {
  button_text: string;
  link: string;
};

export default function ButtonLink({ button_text, link }: MyButtonProps) {
      const router = useRouter();
      return (
        <button
          onClick={() => router.push(link)}
          className="
            bg-blue-200 text-blue-400 font-semibold
            px-6 py-2 rounded-full
            transition-colors duration-300
            border-6 border-transparent
            hover:border-blue-900
          "
        >
          {button_text}
        </button>
      );
    }