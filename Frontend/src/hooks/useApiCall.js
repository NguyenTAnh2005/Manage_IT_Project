import { useState, useEffect } from "react";

/**
 * Custom hook để gọi API và quản lý loading/error state
 * @param {Function} apiCall - Hàm gọi API (async)
 * @param {Array} dependencies - Dependencies array để re-run API call
 * @returns {Object} { data, loading, error }
 */
export const useApiCall = (apiCall, dependencies = []) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let isMounted = true; // Để prevent memory leak

        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);
                const result = await apiCall();
                if (isMounted) {
                    setData(result);
                }
            } catch (err) {
                if (isMounted) {
                    setError(err?.response?.data?.detail || err.message || "Có lỗi xảy ra");
                }
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        };

        fetchData();

        return () => {
            isMounted = false;
        };
    }, dependencies);

    return { data, loading, error };
};
