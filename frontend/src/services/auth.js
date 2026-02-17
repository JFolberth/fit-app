/**
 * Auth helper for SWA EasyAuth.
 * Fetches /.auth/me to get the authenticated user's info and
 * populates the #user-name element in the navbar.
 */

export async function loadUser() {
  try {
    const res = await fetch('/.auth/me');
    if (!res.ok) return null;
    const data = await res.json();
    const user = data.clientPrincipal;
    if (user) {
      const el = document.getElementById('user-name');
      if (el) {
        el.textContent = user.userDetails || user.userId;
      }
    }
    return user;
  } catch {
    return null;
  }
}
