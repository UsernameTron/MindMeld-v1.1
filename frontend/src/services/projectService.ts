import { apiService } from './apiService';
import type { Project } from '../../pages/api/projects/recent';

export const projectService = {
  getRecentProjects: async (): Promise<Project[]> => {
    return apiService.get<Project[]>('/projects/recent');
  }
};
