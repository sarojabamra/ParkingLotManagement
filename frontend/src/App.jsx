import { useCallback, useEffect, useState } from "react";
import {
  AuthError,
  api,
  clearSession,
  getToken,
  getUser,
  saveUser,
  setSession,
  toIstIso,
} from "./api.js";

const PAGES = [
  { id: "availability", label: "Availability" },
  { id: "park", label: "Park / Exit" },
  { id: "bookings", label: "Bookings" },
  { id: "history", label: "My history" },
  { id: "admin", label: "Admin" },
];

function formatValue(value) {
  if (value === null || value === undefined || value === "") return "—";
  return value;
}

function DataTable({ rows, columns, empty = "No records yet." }) {
  if (!rows) return <div className="empty">Loading…</div>;
  if (!rows.length) return <div className="empty">{empty}</div>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.label}>{col.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={row.id ?? index}>
              {columns.map((col) => (
                <td key={col.label}>{formatValue(col.value(row))}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const HISTORY_COLUMNS = [
  { label: "ID", value: (row) => row.id },
  { label: "Vehicle", value: (row) => row.vehicle_number },
  { label: "Type", value: (row) => row.type },
  { label: "Level", value: (row) => row.level },
  { label: "Lot", value: (row) => row.lot },
  { label: "In", value: (row) => row.in_time || row.start_time },
  { label: "Out", value: (row) => row.out_time || row.end_time },
  { label: "Fee", value: (row) => row.fee },
  { label: "Status", value: (row) => row.status },
];

export default function App() {
  const [user, setUser] = useState(() => (getToken() ? getUser() : null));
  const [authTab, setAuthTab] = useState("login");
  const [page, setPage] = useState("availability");
  const [banner, setBanner] = useState(null);
  const [availability, setAvailability] = useState(null);
  const [bookings, setBookings] = useState(null);
  const [history, setHistory] = useState(null);
  const [adminHistory, setAdminHistory] = useState(null);
  const [lockResult, setLockResult] = useState(null);

  const showBanner = (message, type) => setBanner({ message, type });

  const handleError = useCallback((error) => {
    if (error instanceof AuthError) {
      setUser(null);
    }
    showBanner(error.message, "err");
  }, []);

  const loadAvailability = useCallback(async () => {
    try {
      setAvailability(await api("/parking/availability"));
    } catch (error) {
      setAvailability([]);
      handleError(error);
    }
  }, [handleError]);

  const loadBookings = useCallback(async () => {
    try {
      setBookings(await api("/bookings/"));
    } catch (error) {
      setBookings([]);
      handleError(error);
    }
  }, [handleError]);

  const loadHistory = useCallback(async () => {
    try {
      setHistory(await api("/parking/history"));
    } catch (error) {
      setHistory([]);
      handleError(error);
    }
  }, [handleError]);

  const loadAdminHistory = useCallback(
    async (vehicleNumber) => {
      try {
        const path = vehicleNumber
          ? `/admin/parking-history/${encodeURIComponent(vehicleNumber)}`
          : "/admin/parking-history";
        setAdminHistory(await api(path));
      } catch (error) {
        setAdminHistory([]);
        handleError(error);
      }
    },
    [handleError],
  );

  useEffect(() => {
    if (!user) return;
    if (page === "availability") loadAvailability();
    if (page === "bookings") loadBookings();
    if (page === "history") loadHistory();
    if (page === "admin") loadAdminHistory();
  }, [user, page, loadAvailability, loadBookings, loadHistory, loadAdminHistory]);

  async function onLogin(event) {
    event.preventDefault();
    const form = new FormData(event.target);
    try {
      const data = await api("/auth/login", {
        method: "POST",
        body: new URLSearchParams({
          username: form.get("username"),
          password: form.get("password"),
        }),
      });
      setUser(setSession(data.access_token, form.get("username")));
      setPage("availability");
      showBanner("Logged in.", "ok");
    } catch (error) {
      handleError(error);
    }
  }

  async function onRegister(event) {
    event.preventDefault();
    const form = new FormData(event.target);
    try {
      const created = await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          name: form.get("name"),
          password: form.get("password"),
        }),
      });
      setAuthTab("login");
      showBanner(
        `Account created for ${created.name} (id ${created.id}). You can log in now.`,
        "ok",
      );
    } catch (error) {
      handleError(error);
    }
  }

  function onLogout() {
    clearSession();
    setUser(null);
    setBanner(null);
    setAvailability(null);
    setBookings(null);
    setHistory(null);
    setAdminHistory(null);
    setLockResult(null);
  }

  async function onLock(event) {
    event.preventDefault();
    const form = new FormData(event.target);
    try {
      const result = await api("/parking/lock", {
        method: "POST",
        body: JSON.stringify({
          vehicle_number: form.get("vehicle_number"),
          level: Number(form.get("level")),
          type: form.get("type"),
        }),
      });
      setLockResult(result);
      showBanner(
        `Locked lot ${result.lot} on level ${result.level} for ${result.vehicle_number}.`,
        "ok",
      );
    } catch (error) {
      handleError(error);
    }
  }

  async function onUnlock(event) {
    event.preventDefault();
    const form = new FormData(event.target);
    try {
      const result = await api("/parking/unlock", {
        method: "POST",
        body: JSON.stringify({
          vehicle_number: form.get("vehicle_number"),
          level: Number(form.get("level")),
          lot: Number(form.get("lot")),
        }),
      });
      showBanner(`Unlocked lot ${result.lot}. Fee: ${result.parking_fee}.`, "ok");
    } catch (error) {
      handleError(error);
    }
  }

  async function onBook(event) {
    event.preventDefault();
    const form = new FormData(event.target);
    try {
      const result = await api("/bookings/", {
        method: "POST",
        body: JSON.stringify({
          vehicle_number: form.get("vehicle_number"),
          level: Number(form.get("level")),
          type: form.get("type"),
          start_time: toIstIso(form.get("start_time")),
          end_time: toIstIso(form.get("end_time")),
        }),
      });
      event.target.reset();
      showBanner(`Booking ${result.id} created for lot ${result.lot}.`, "ok");
      loadBookings();
    } catch (error) {
      handleError(error);
    }
  }

  async function onCancelBooking(bookingId) {
    try {
      await api(`/bookings/${bookingId}`, { method: "DELETE" });
      showBanner("Booking cancelled.", "ok");
      loadBookings();
    } catch (error) {
      handleError(error);
    }
  }

  async function onCreateSpace(event) {
    event.preventDefault();
    const form = new FormData(event.target);
    try {
      const result = await api("/admin/parking-spaces", {
        method: "POST",
        body: JSON.stringify({
          level: Number(form.get("level")),
          twa: Number(form.get("twa")),
          fwa: Number(form.get("fwa")),
        }),
      });
      event.target.reset();
      showBanner(`Created level ${result.level}.`, "ok");
    } catch (error) {
      handleError(error);
    }
  }

  async function onPromote(event) {
    event.preventDefault();
    const form = new FormData(event.target);
    const userId = form.get("user_id");
    try {
      const result = await api(`/admin/users/${userId}/role`, { method: "PATCH" });
      showBanner(`${result.name} is now ${result.role}.`, "ok");
      if (user && String(user.id) === String(result.id)) {
        const next = { ...user, role: result.role };
        saveUser(next);
        setUser(next);
      }
    } catch (error) {
      handleError(error);
    }
  }

  async function onVehicleSearch(event) {
    event.preventDefault();
    const vehicleNumber = new FormData(event.target).get("vehicle_number").trim();
    loadAdminHistory(vehicleNumber);
  }

  async function onUserHistorySearch(event) {
    event.preventDefault();
    const userId = new FormData(event.target).get("user_id").trim();
    if (!userId) {
      loadHistory();
      return;
    }
    try {
      setHistory(await api(`/parking/users/${userId}/history`));
    } catch (error) {
      setHistory([]);
      handleError(error);
    }
  }

  const isAdmin = user?.role === "ADMIN";

  return (
    <>
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <div>
            <h1>Parking Lot</h1>
            <p>Manage spots, bookings, and history</p>
          </div>
        </div>
        {user && (
          <div className="session-bar">
            <span>
              {user.username} · {user.role} · id {user.id}
            </span>
            <button type="button" className="btn btn-ghost" onClick={onLogout}>
              Log out
            </button>
          </div>
        )}
      </header>

      <main>
        {banner && (
          <p className={`banner ${banner.type}`} role="status">
            {banner.message}
          </p>
        )}

        {!user && (
          <section className="card auth-card">
            <div className="tabs">
              <button
                type="button"
                className={`tab ${authTab === "login" ? "active" : ""}`}
                onClick={() => setAuthTab("login")}
              >
                Login
              </button>
              <button
                type="button"
                className={`tab ${authTab === "register" ? "active" : ""}`}
                onClick={() => setAuthTab("register")}
              >
                Register
              </button>
            </div>

            {authTab === "login" ? (
              <form className="form" onSubmit={onLogin}>
                <label>
                  Username
                  <input name="username" autoComplete="username" required />
                </label>
                <label>
                  Password
                  <input
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                  />
                </label>
                <button type="submit" className="btn btn-primary">
                  Login
                </button>
              </form>
            ) : (
              <form className="form" onSubmit={onRegister}>
                <label>
                  Username
                  <input name="name" autoComplete="username" required />
                </label>
                <label>
                  Password
                  <input
                    name="password"
                    type="password"
                    autoComplete="new-password"
                    required
                  />
                </label>
                <button type="submit" className="btn btn-primary">
                  Create account
                </button>
              </form>
            )}
          </section>
        )}

        {user && (
          <>
            <nav className="tabs page-tabs">
              {PAGES.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={`tab ${page === item.id ? "active" : ""}`}
                  onClick={() => setPage(item.id)}
                >
                  {item.label}
                </button>
              ))}
            </nav>

            {page === "availability" && (
              <section className="card">
                <div className="page-head">
                  <h2>Availability</h2>
                  <button type="button" className="btn" onClick={loadAvailability}>
                    Refresh
                  </button>
                </div>
                <DataTable
                  rows={availability}
                  empty="No parking levels yet. An admin can create one."
                  columns={[
                    { label: "Level", value: (row) => row.level },
                    {
                      label: "Two-wheeler",
                      value: (row) =>
                        isAdmin
                          ? row.two_wheeler_available
                          : row.two_wheeler_available
                            ? "Available"
                            : "Full",
                    },
                    {
                      label: "Four-wheeler",
                      value: (row) =>
                        isAdmin
                          ? row.four_wheeler_available
                          : row.four_wheeler_available
                            ? "Available"
                            : "Full",
                    },
                  ]}
                />
              </section>
            )}

            {page === "park" && (
              <section className="card">
                <h2>Park now</h2>
                <form className="form grid" onSubmit={onLock}>
                  <label>
                    Vehicle number
                    <input name="vehicle_number" required placeholder="MP09 8282" />
                  </label>
                  <label>
                    Level
                    <input name="level" type="number" min="1" required />
                  </label>
                  <label>
                    Type
                    <select name="type" defaultValue="TW">
                      <option value="TW">Two-wheeler</option>
                      <option value="FW">Four-wheeler</option>
                    </select>
                  </label>
                  <button type="submit" className="btn btn-primary">
                    Lock spot
                  </button>
                </form>
                {lockResult && (
                  <p className="lot-result">
                    Assigned lot <strong>{lockResult.lot}</strong> at{" "}
                    {lockResult.locking_time}
                  </p>
                )}

                <h2>Exit / unlock</h2>
                <form className="form grid" onSubmit={onUnlock}>
                  <label>
                    Vehicle number
                    <input name="vehicle_number" required />
                  </label>
                  <label>
                    Level
                    <input name="level" type="number" min="1" required />
                  </label>
                  <label>
                    Lot
                    <input name="lot" type="number" min="1" required />
                  </label>
                  <button type="submit" className="btn btn-primary">
                    Unlock spot
                  </button>
                </form>
              </section>
            )}

            {page === "bookings" && (
              <section className="card">
                <h2>Create booking</h2>
                <form className="form grid" onSubmit={onBook}>
                  <label>
                    Vehicle number
                    <input name="vehicle_number" required />
                  </label>
                  <label>
                    Level
                    <input name="level" type="number" min="1" required />
                  </label>
                  <label>
                    Type
                    <select name="type" defaultValue="TW">
                      <option value="TW">Two-wheeler</option>
                      <option value="FW">Four-wheeler</option>
                    </select>
                  </label>
                  <label>
                    Start time
                    <input name="start_time" type="datetime-local" required />
                  </label>
                  <label>
                    End time
                    <input name="end_time" type="datetime-local" required />
                  </label>
                  <button type="submit" className="btn btn-primary">
                    Book
                  </button>
                </form>

                <div className="page-head">
                  <h2>My bookings</h2>
                  <button type="button" className="btn" onClick={loadBookings}>
                    Refresh
                  </button>
                </div>
                <DataTable
                  rows={bookings}
                  empty="No bookings yet."
                  columns={[
                    { label: "ID", value: (row) => row.id },
                    { label: "Vehicle", value: (row) => row.vehicle_number },
                    { label: "Type", value: (row) => row.type },
                    { label: "Level", value: (row) => row.level },
                    { label: "Lot", value: (row) => row.lot },
                    {
                      label: "Start",
                      value: (row) => row.start_time || row.in_time,
                    },
                    {
                      label: "End",
                      value: (row) => row.end_time || row.scheduled_out_time,
                    },
                    { label: "Status", value: (row) => row.status },
                    {
                      label: "",
                      value: (row) => (
                        <button
                          type="button"
                          className="btn"
                          onClick={() => onCancelBooking(row.id)}
                        >
                          Cancel
                        </button>
                      ),
                    },
                  ]}
                />
              </section>
            )}

            {page === "history" && (
              <section className="card">
                <div className="page-head">
                  <h2>My parking history</h2>
                  <button type="button" className="btn" onClick={loadHistory}>
                    Refresh
                  </button>
                </div>
                <form className="form inline" onSubmit={onUserHistorySearch}>
                  <label>
                    User ID
                    <input
                      name="user_id"
                      type="number"
                      min="1"
                      placeholder={user?.id ? String(user.id) : "User id"}
                    />
                  </label>
                  <button type="submit" className="btn">
                    Load by user id
                  </button>
                </form>
                <DataTable rows={history} columns={HISTORY_COLUMNS} />
              </section>
            )}

            {page === "admin" && (
              <section className="card">
                <h2>Create parking level</h2>
                <form className="form grid" onSubmit={onCreateSpace}>
                  <label>
                    Level
                    <input name="level" type="number" min="1" required />
                  </label>
                  <label>
                    Two-wheeler spots
                    <input name="twa" type="number" min="0" required />
                  </label>
                  <label>
                    Four-wheeler spots
                    <input name="fwa" type="number" min="0" required />
                  </label>
                  <button type="submit" className="btn btn-primary">
                    Create level
                  </button>
                </form>

                <h2>Promote user to admin</h2>
                <form className="form grid" onSubmit={onPromote}>
                  <label>
                    User ID
                    <input name="user_id" type="number" min="1" required />
                  </label>
                  <button type="submit" className="btn btn-primary">
                    Promote
                  </button>
                </form>

                <div className="page-head">
                  <h2>All parking history</h2>
                  <button type="button" className="btn" onClick={() => loadAdminHistory()}>
                    Refresh
                  </button>
                </div>
                <form className="form inline" onSubmit={onVehicleSearch}>
                  <label>
                    Vehicle number
                    <input name="vehicle_number" placeholder="Filter by vehicle" />
                  </label>
                  <button type="submit" className="btn">
                    Search
                  </button>
                </form>
                <DataTable
                  rows={adminHistory}
                  columns={[{ label: "User", value: (row) => row.user_id }, ...HISTORY_COLUMNS]}
                />
              </section>
            )}
          </>
        )}
      </main>
    </>
  );
}
