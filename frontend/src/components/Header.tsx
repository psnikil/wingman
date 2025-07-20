'use client';

import { useRouter } from 'next/navigation';
import { useBackendStore } from '@/store/backendStore'; // Update path if needed

export default function Header() {
  const router = useRouter();
  const { backendInit } = useBackendStore();

  const handleLogoClick = () => {
    router.push(backendInit ? '/homepage' : '/');
  };

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b-gray-800">
      <div className="flex items-center gap-2">
        <span
          onClick={handleLogoClick}
          className="text-xl font-bold text-blue-400 tracking-wide select-none cursor-pointer flex items-center gap-2"
        >
          <img src="/logo.svg" alt="Logo" className="h-20 w-auto p-2" />
          WINGMAN
        </span>
      </div>
      <div className="flex items-center">
        <span className="w-9 h-9 flex items-center justify-center rounded-full bg-blue-500 text-white font-bold text-lg">
          U
        </span>
      </div>
    </header>
  );
}
