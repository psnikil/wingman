import { create } from 'zustand';

type BackendStore = {
  backendInit: boolean;
  setBackendInit: (value: boolean) => void;
};

type OllamaStore= {
  ollamaInit: boolean,
  setOllamaInit:(value:boolean) =>void;
}

type DbStore= {
  dbInit: boolean,
  setDbInit:(value:boolean) =>void;
}

type LLMstore= {
  chosen_llm: string,
  available_llms: string[],
  setLLMstore: (value: string[]) => void,
  setChosenLLM: (value: string) => void
}

export const useBackendStore = create<BackendStore>((set) => ({
  backendInit: false,
  setBackendInit: (value) => set({ backendInit: value }),
}));

export const useOllamaInitStore =  create<OllamaStore>((set) => ({
  ollamaInit: false,
  setOllamaInit:(value) => set({ollamaInit: value})
}))

export const useDbInitStore =  create<DbStore>((set) => ({
  dbInit: false,
  setDbInit:(value) => set({dbInit: value})
}))

export const useLLMstore =  create<LLMstore>((set) => ({
  chosen_llm: '',
  available_llms: [],
  setLLMstore:(value) => set({available_llms:value}),
  setChosenLLM:(value) => set({chosen_llm:value}),

}))



