export const DEMO_MODE =
  process.env.NEXT_PUBLIC_DEMO_MODE === "true";

export function isDemoMode(): boolean {
  return DEMO_MODE;
}

export function demoModeLabel(): string {
  return DEMO_MODE
    ? "Demo Mode"
    : "Live Mode";
}
