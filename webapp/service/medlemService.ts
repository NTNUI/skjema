const API_URL = 'http://localhost:8000'
const TOKEN_URL = `${API_URL}/token/`
const PROFILE_URL = `${API_URL}/users/profile/`
const GROUPS_URL = `${API_URL}/groups/`


export const fetchToken = async (phoneNumber: string, password: string): Promise<string> => {
    const body = {"phone_number": phoneNumber, "password": password}
    const response = await fetch(TOKEN_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            },
        body: JSON.stringify(body),
    });

    if (!response.ok) throw "Kunne ikke finne brukeren."
    const responseBody = await response.json();
    return responseBody.access
}

export const fetchProfile = async (token: string) => {
    const response = await fetch(PROFILE_URL, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
    })
    if (!response.ok) throw "Kunne ikke hente brukerdata."
    return await response.json();
}

export const updateProfile = async (token: string, accountNumber: string) => {
    const response = await fetch(PROFILE_URL, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
            },
        body: JSON.stringify({"bank_account_number": accountNumber}),
    });
    await response;
}

export const fetchGroups = async () => {
    try {
        const response = await fetch(GROUPS_URL)
        if (!response.ok) return []
        const responseBody = await response.json()
        return responseBody.results
    }
    catch {
        return []
    }
}
