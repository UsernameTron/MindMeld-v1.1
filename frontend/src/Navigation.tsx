import { useRouter } from 'next/navigation';
import { useAuth } from './AuthContext';

export const Navigation: React.FC = () => {
  const { logout, isAuthenticated } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.replace('/login');
  };

  if (!isAuthenticated) return null;

  return (
    <nav className="bg-primary text-white p-4">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-bold">MyApp</h1>
        <button 
          onClick={handleLogout}
          className="px-4 py-2 rounded bg-white text-primary hover:bg-gray-100"
        >
          Logout
        </button>
      </div>
    </nav>
  );
};
