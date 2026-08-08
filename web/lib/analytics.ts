export type AnalyticsEventName =
  | "problem_page_view"
  | "tool_started"
  | "task_entered"
  | "first_step_generated"
  | "smaller_step_requested"
  | "next_step_requested"
  | "signup_clicked"
  | "app_continue_clicked"
  | "paywall_viewed"
  | "purchase_started";

export type AnalyticsPayload = Record<
  string,
  string | number | boolean | null | undefined
>;

declare global {
  interface Window {
    dataLayer?: Array<Record<string, unknown>>;
  }
}

export function trackEvent(
  event: AnalyticsEventName,
  payload: AnalyticsPayload = {},
): void {
  if (typeof window === "undefined") return;

  const record = {
    event,
    ...payload,
    occurred_at: new Date().toISOString(),
  };

  // Vendor-neutral event stream. Google Tag Manager / another analytics provider
  // can consume dataLayer later without changing Product Page code.
  window.dataLayer?.push(record);
  window.dispatchEvent(
    new CustomEvent("vmeste:analytics", {
      detail: record,
    }),
  );
}
