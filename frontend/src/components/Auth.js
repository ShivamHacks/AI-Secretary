import { useEffect } from "react";
import Cookies from 'js-cookie';
import { useDataContext } from "./DataProvider";

const COOKIE_STRING = "userInfo";

const verifyAccessToken = async (accessToken) => {
    try {
        const response = await fetch(`https://oauth2.googleapis.com/tokeninfo?access_token=${accessToken}`);
        const data = await response.json();
        if (data.error) {
            console.error('Invalid Access Token:', data.error_description);
            return false;
        } else {
            console.log('Valid Access Token:', data);
            return true;
        }
    } catch (error) {
        console.error('Error verifying access token:', error);
        return false;
    }
};

const getEmail = async (accessToken) => {
    try {
        const response = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        if (!response.ok) {
            console.log(`Failed to fetch user info: ${response}`);
            return null;
        }

        const data = await response.json();
        console.log('User Info:', data);
        console.log('Email:', data.email);
        if (data && data.email) {
            return data.email;
        }
    } catch (error) {
        console.error('Error fetching user info:', error);
    }
    return null;
};

const getStoredUserData = async () => {
    const storedUserInfo = Cookies.get(COOKIE_STRING);
    if (!storedUserInfo) {
        console.log("No stored user info found");
        return null;
    }
    const userInfo = JSON.parse(storedUserInfo);
    console.log("Stored user info:", userInfo);
    if (!userInfo || !userInfo.accessToken || !userInfo.email) {
        console.log("User info cookie is invalid");
        return null;
    }
    const isTokenValid = await verifyAccessToken(userInfo.accessToken);
    if (!isTokenValid) {
        console.log("Access token in cookie is invalid");
        return null;
    }
    const emailFromToken = await getEmail(userInfo.accessToken);
    if (userInfo.email !== emailFromToken) {
        console.log("Email in cookie is invalid");
        return null;
    }
    console.log("User info cookie is valid");
    return userInfo;
};

function Auth() {
    const { setUserInfo } = useDataContext();

    const handleClick = () => {
        // TODO(security): do token storage and authentication on server.
        // So redirect to server when logging in and then redirect back to frontend
        // with a session token that can be used to authenticate requests.
        const callbackUrl = `${window.location.origin}`;
        const googleClientId = "162392179468-piehbrgd3hfo1l8v63hn39sp1cdrof83.apps.googleusercontent.com";
        const scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ];
        const targetUrl = `https://accounts.google.com/o/oauth2/auth?redirect_uri=${encodeURIComponent(
            callbackUrl
        )}&response_type=token&client_id=${googleClientId}&scope=${encodeURIComponent(scopes.join(' '))}`;
        window.location.href = targetUrl;
    };

    useEffect(() => {
        const fetchAndStoreUserInfo = async () => {
            // Checks if Google auth redirected to this page with access token
            const accessTokenRegex = /access_token=([^&]+)/;
            const isMatch = window.location.href.match(accessTokenRegex);
            if (!isMatch) {
                // We are in the root url, try getting user info from cookies
                const storedUserInfo = await getStoredUserData();
                if (storedUserInfo) {
                    // We have stored info, set info and let state cause redirect to app
                    setUserInfo(storedUserInfo);
                }
                // Regardless of if cookies are stored or not, we stay at the root url because
                // if the user info state is set, the root App component will load the main app,
                // otherwise we show the login button.
                return;
            }
            // We were redirected from google auth with access token
            const accessToken = isMatch[1];
            const isTokenValid = await verifyAccessToken(accessToken);
            if (!isTokenValid) {
                // Try logging in again, i.e. removing access token from url
                console.error(`Invalid Access Token: ${accessToken}`);
                window.location.href = window.location.origin;
                return;
            }
            const email = await getEmail(accessToken);
            if (!email) {
                // Try logging in again, i.e. removing access token from url
                console.error('Failed to fetch user email');
                window.location.href = window.location.origin;
                return;
            }
            // Store user info in cookies
            const userInfo = {
                "accessToken": accessToken,
                "email": email,
            }
            console.log('Storing user info:', userInfo);
            Cookies.set(COOKIE_STRING, JSON.stringify(userInfo));
            setUserInfo(userInfo);
            window.location.href = window.location.origin;
        };

        fetchAndStoreUserInfo();
    }, []);

    return (
        <div className="root">
            <div>
                <div className="btn-container">
                    <button className="btn btn-primary" onClick={handleClick}>
                        Log in with Google
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Auth;
