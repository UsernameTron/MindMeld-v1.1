// Mock version of the shims/navigation.ts file
import { useRouter, routerFunctions } from '../../__tests__/test-utils/RouterWrapper';

// Export the test router implementation directly
export { useRouter, routerFunctions };
export default { useRouter, ...routerFunctions };
