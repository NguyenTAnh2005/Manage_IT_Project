/**
 * Custom hook to extract current user info from AuthContext.
 * Handles fragile nested user object structures.
 * 
 * @returns {Object} - { id, name, email }
 */
export const useCurrentUser = (currentUser) => {
    if (!currentUser) return { id: null, name: "Unknown", email: null };
    
    // Try multiple possible ID paths (user object variations)
    const id = currentUser?.id || currentUser?.user_id || currentUser?.data?.id;
    
    // Try multiple possible name paths
    const name = currentUser?.full_name || currentUser?.name || currentUser?.username || "Ẩn danh";
    
    // Try multiple possible email paths
    const email = currentUser?.email || currentUser?.data?.email;
    
    return { id, name, email };
};
