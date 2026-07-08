import { greeting } from "./lib/greeting";

export function App(): JSX.Element {
  return (
    <main>
      <h1>{greeting("sample-app")}</h1>
      <p>AOD 対象プロダクトの雛形(React + Vite + TypeScript)</p>
    </main>
  );
}
