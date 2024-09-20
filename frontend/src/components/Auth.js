import { useState, useEffect } from "react";
import Cookies from 'js-cookie';


function Auth({ setToken }) {
    const handleClick = () => {
        // TODO(security): do token storage and authentication on server.
        // So redirect to server when logging in and then redirect back to frontend
        // with a session token that can be used to authenticate requests.
        const callbackUrl = `${window.location.origin}`;
        const googleClientId = "162392179468-piehbrgd3hfo1l8v63hn39sp1cdrof83.apps.googleusercontent.com";
        const scope = "https://www.googleapis.com/auth/calendar";
        const targetUrl = `https://accounts.google.com/o/oauth2/auth?redirect_uri=${encodeURIComponent(
            callbackUrl
        )}&response_type=token&client_id=${googleClientId}&scope=${encodeURIComponent(scope)}`;
        window.location.href = targetUrl;
    };

    useEffect(() => {
        // Checks if Google auth redirected to this page with access token
        const accessTokenRegex = /access_token=([^&]+)/;
        const isMatch = window.location.href.match(accessTokenRegex);
        if (isMatch) {
            const accessToken = isMatch[1];
            Cookies.set("accessToken", accessToken);
            console.log("Access token set:", Cookies.get("accessToken"));
            setToken(accessToken);
            window.location.href = window.location.origin;
        } else {
            // First time page is loaded, remove access token for testing
            Cookies.remove("accessToken");
        }
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
