import { useNavStore } from '@/state/navStore';

export const nexusFetch = async (url: string, options: RequestInit = {}) => {
    const { activeTenant, activeRole } = useNavStore.getState();
    const headers = { 
        ...options.headers, 
        'X-Nexus-Tenant': activeTenant, 
        'X-Nexus-Role': activeRole 
    };
    return fetch(url, { ...options, headers });
};
