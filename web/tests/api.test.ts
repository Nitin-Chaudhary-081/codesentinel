import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";

// Simple utility tests that don't require Next.js runtime
import { LANGUAGES } from "@/lib/api";

describe("API utilities", () => {
  test("LANGUAGES contains all 6 supported languages", () => {
    expect(LANGUAGES).toHaveLength(6);
    const values = LANGUAGES.map((l) => l.value);
    expect(values).toContain("typescript");
    expect(values).toContain("python");
    expect(values).toContain("go");
    expect(values).toContain("java");
    expect(values).toContain("javascript");
    expect(values).toContain("cpp");
  });

  test("each language has a label", () => {
    LANGUAGES.forEach((lang) => {
      expect(lang.label).toBeTruthy();
      expect(lang.value).toBeTruthy();
    });
  });
});
