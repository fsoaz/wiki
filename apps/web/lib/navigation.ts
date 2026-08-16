export function safeNextPath(value: string): string {
  let decoded: string;
  try {
    decoded = decodeURIComponent(value);
  } catch {
    return "/";
  }
  if (!value.startsWith("/") || value.startsWith("//") || decoded.startsWith("//")) {
    return "/";
  }
  if (
    value.includes("\\") ||
    decoded.includes("\\") ||
    /[\u0000-\u001f\u007f]/.test(decoded)
  ) {
    return "/";
  }
  return value;
}
