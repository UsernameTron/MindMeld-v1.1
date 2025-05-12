// Use our custom router implementation for tests
// This allows us to export either the real Next.js router or our test mock
// depending on the environment
import { useRouter as nextUseRouter } from "next/navigation";
import { useRouter as testUseRouter } from "../__tests__/test-utils/RouterWrapper";

// Export the correct implementation based on environment
export const useRouter = typeof process !== "undefined" && process.env.NODE_ENV === "test" 
  ? testUseRouter 
  : nextUseRouter;
