import { create } from 'zustand';

type BackendStore = {
  backendInit: boolean;
  setBackendInit: (value: boolean) => void;
};

export const useBackendStore = create<BackendStore>((set) => ({
  backendInit: false,
  setBackendInit: (value) => set({ backendInit: value }),
}));
