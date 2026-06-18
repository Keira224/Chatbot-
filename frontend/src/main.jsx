import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Bell,
  Bot,
  CalendarDays,
  Check,
  ChevronLeft,
  ChevronRight,
  CircleUserRound,
  Clock3,
  LayoutDashboard,
  LogOut,
  Menu,
  Pencil,
  Plus,
  Search,
  Settings2,
  Trash2,
  Users,
  X,
} from "lucide-react";
import "./styles.css";

const rootElement = document.querySelector("#root");

function getCookie(name) {
  const item = document.cookie
    .split(";")
    .map((value) => value.trim())
    .find((value) => value.startsWith(`${name}=`));
  return item ? decodeURIComponent(item.split("=").slice(1).join("=")) : "";
}

async function api(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
      ...options.headers,
    },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.detail || "Une erreur est survenue.");
    error.data = data;
    throw error;
  }
  return data;
}

function formatDate(value, options = {}) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "short",
    year: options.short ? undefined : "numeric",
  }).format(new Date(`${value}T12:00:00`));
}

function formatDateTime(value) {
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function initials(user) {
  const value = `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.username;
  return value
    .split(" ")
    .slice(0, 2)
    .map((item) => item[0])
    .join("")
    .toUpperCase();
}

function WorkspaceShell({ user, navigation, activeView, onNavigate, children }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  async function logout() {
    await fetch("/accounts/api/auth/deconnexion/", {
      method: "POST",
      credentials: "same-origin",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
    });
    window.location.href = "/";
  }

  return (
    <div className="workspace">
      <aside className={`workspace-sidebar ${mobileOpen ? "is-open" : ""}`}>
        <div className="workspace-brand">
          <span className="brand-mark">A</span>
          <div>
            <strong>AcadReminder</strong>
            <small>{user.is_staff ? "Administration" : "Espace academique"}</small>
          </div>
          <button className="icon-button sidebar-close" onClick={() => setMobileOpen(false)} aria-label="Fermer le menu">
            <X size={19} />
          </button>
        </div>

        <nav className="workspace-nav" aria-label="Navigation principale">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={activeView === item.id ? "is-active" : ""}
                onClick={() => {
                  onNavigate(item.id);
                  setMobileOpen(false);
                }}
              >
                <Icon size={18} />
                <span>{item.label}</span>
                {item.badge > 0 && <b>{item.badge}</b>}
              </button>
            );
          })}
        </nav>

        <div className="workspace-account">
          <span className="account-avatar">{initials(user)}</span>
          <div>
            <strong>{user.first_name || user.username}</strong>
            <small>{user.is_staff ? "Administrateur" : user.role_label}</small>
          </div>
          <button className="icon-button" onClick={logout} title="Deconnexion" aria-label="Deconnexion">
            <LogOut size={18} />
          </button>
        </div>
      </aside>

      {mobileOpen && <button className="sidebar-backdrop" onClick={() => setMobileOpen(false)} aria-label="Fermer le menu" />}

      <main className="workspace-main">
        <header className="workspace-mobile-header">
          <button className="icon-button" onClick={() => setMobileOpen(true)} aria-label="Ouvrir le menu">
            <Menu size={21} />
          </button>
          <strong>AcadReminder</strong>
          <span className="account-avatar account-avatar-small">{initials(user)}</span>
        </header>
        {children}
      </main>
    </div>
  );
}

function PageHeader({ eyebrow, title, description, action }) {
  return (
    <header className="page-header">
      <div>
        <span>{eyebrow}</span>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action}
    </header>
  );
}

function Metric({ label, value, detail, icon: Icon }) {
  return (
    <div className="metric">
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{detail}</small>
      </div>
      <Icon size={20} />
    </div>
  );
}

function StatusBadge({ urgency, children }) {
  return <span className={`status status-${urgency}`}>{children}</span>;
}

function StudentApp({ user }) {
  const requestedView = new URLSearchParams(window.location.search).get("view");
  const initialView = ["monthly", "calendar", "home", "assistant", "notifications", "preferences", "profile"].includes(requestedView)
    ? requestedView
    : "monthly";
  const [view, setView] = useState(initialView);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);

  async function load() {
    try {
      setLoading(true);
      const result = await api("/accounts/api/etudiant/");
      setData(result);
      setChatMessages(result.chat_messages);
      setError("");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const navigation = [
    { id: "monthly", label: "Vue mensuelle", icon: CalendarDays },
    { id: "calendar", label: "Tous les evenements", icon: CalendarDays },
    { id: "home", label: "Vue d'ensemble", icon: LayoutDashboard },
    { id: "assistant", label: "Assistant", icon: Bot },
    { id: "notifications", label: "Notifications", icon: Bell, badge: data?.summary.unread_notifications || 0 },
    { id: "preferences", label: "Mes rappels", icon: Settings2 },
    { id: "profile", label: "Mon profil", icon: CircleUserRound },
  ];

  return (
    <WorkspaceShell user={user} navigation={navigation} activeView={view} onNavigate={setView}>
      {loading && <LoadingState />}
      {error && <ErrorState message={error} onRetry={load} />}
      {data && view === "home" && <StudentOverview user={user} data={data} onNavigate={setView} />}
      {data && view === "monthly" && <AcademicMonthlyCalendar events={data.events} onNavigate={setView} />}
      {data && view === "calendar" && <StudentCalendar events={data.events} eventTypes={data.event_types} onNavigate={setView} />}
      {data && view === "assistant" && <StudentAssistant messages={chatMessages} setMessages={setChatMessages} />}
      {data && view === "notifications" && <StudentNotifications data={data} onRefresh={load} />}
      {data && view === "preferences" && <StudentPreferences data={data} onRefresh={load} />}
      {data && view === "profile" && <AcademicProfile user={user} />}
      {data && view !== "assistant" && (
        <>
          <button className="chat-launcher" onClick={() => setChatOpen(true)}>
            <Bot size={19} />
            <span>Assistant</span>
          </button>
          {chatOpen && (
            <ChatDrawer
              messages={chatMessages}
              setMessages={setChatMessages}
              onClose={() => setChatOpen(false)}
              onExpand={() => {
                setChatOpen(false);
                setView("assistant");
              }}
            />
          )}
        </>
      )}
    </WorkspaceShell>
  );
}

function StudentOverview({ user, data, onNavigate }) {
  const nextEvent = data.summary.next_event;
  const urgentEvents = data.upcoming_events.filter((event) => event.days_until >= 0 && event.days_until <= 7).slice(0, 4);

  return (
    <div className="page">
      <PageHeader
        eyebrow={`Espace academique · ${user.role_label}`}
        title={`Bonjour ${user.first_name || user.username}`}
        description="Les prochaines dates et rappels utiles, sans bruit."
        action={
          <button className="button button-primary" onClick={() => onNavigate("assistant")}>
            <Bot size={17} /> Poser une question
          </button>
        }
      />

      <div className="metrics-grid">
        <Metric label="A venir" value={data.summary.upcoming_events} detail="evenements programmes" icon={CalendarDays} />
        <Metric label="Non lues" value={data.summary.unread_notifications} detail="notifications a consulter" icon={Bell} />
        <Metric
          label="Prochaine date"
          value={nextEvent ? formatDate(nextEvent.start_date, { short: true }) : "-"}
          detail={nextEvent?.title || "Aucune echeance"}
          icon={Clock3}
        />
      </div>

      <div className="content-grid">
        <section className="content-section">
          <div className="section-heading">
            <div>
              <h2>Prochaines echeances</h2>
              <p>Les dates les plus proches de votre calendrier.</p>
            </div>
            <button className="text-button" onClick={() => onNavigate("calendar")}>
              Tout voir <ChevronRight size={16} />
            </button>
          </div>
          <div className="event-list">
            {data.upcoming_events.slice(0, 5).map((event) => (
              <div className="event-row" key={event.id}>
                <div className="date-tile">
                  <strong>{new Date(`${event.start_date}T12:00:00`).getDate()}</strong>
                  <span>{formatDate(event.start_date, { short: true }).split(" ")[1]}</span>
                </div>
                <div className="event-row-main">
                  <strong>{event.title}</strong>
                  <span>{event.event_type_label} · {event.location || "Lieu non precise"}</span>
                </div>
                <StatusBadge urgency={event.urgency}>{event.status}</StatusBadge>
              </div>
            ))}
          </div>
        </section>

        <section className="content-section">
          <div className="section-heading">
            <div>
              <h2>Cette semaine</h2>
              <p>Les elements qui demandent votre attention.</p>
            </div>
          </div>
          <div className="compact-list">
            {urgentEvents.length ? urgentEvents.map((event) => (
              <div key={event.id}>
                <span className={`priority-dot priority-${event.urgency}`} />
                <div>
                  <strong>{event.title}</strong>
                  <small>{event.status} · {formatDate(event.start_date)}</small>
                </div>
              </div>
            )) : <EmptyInline text="Aucune urgence dans les 7 prochains jours." />}
          </div>
        </section>
      </div>
    </div>
  );
}

function StudentCalendar({ events, eventTypes, onNavigate }) {
  const [query, setQuery] = useState("");
  const [type, setType] = useState("");
  const filtered = useMemo(
    () => events.filter((event) => {
      const matchesQuery = `${event.title} ${event.description} ${event.location}`.toLowerCase().includes(query.toLowerCase());
      return matchesQuery && (!type || event.event_type === type);
    }),
    [events, query, type],
  );
  const typeStats = eventTypes
    .map((item) => ({
      ...item,
      count: events.filter((event) => event.event_type === item.value).length,
    }))
    .filter((item) => item.count > 0);

  return (
    <div className="page student-calendar-page">
      <PageHeader
        eyebrow="Calendrier academique"
        title="Evenements importants"
        description="Toutes les dates publiees par l'administration."
        action={
          <div className="page-actions">
            <button className="button button-primary" onClick={() => onNavigate("monthly")}>
              <CalendarDays size={17} /> Vue mensuelle
            </button>
            <a className="button button-secondary" href="/calendrier/export.ics">
              Exporter le calendrier
            </a>
          </div>
        }
      />

      <div className="event-type-stats">
        {typeStats.map((item) => (
          <button
            className={type === item.value ? "is-active" : ""}
            key={item.value}
            onClick={() => setType(type === item.value ? "" : item.value)}
          >
            <span>{item.label}</span>
            <strong>{item.count}</strong>
          </button>
        ))}
      </div>

      <div className="calendar-filter-panel">
        <label className="filter-field">
          <span>Recherche</span>
          <div className="search-control">
            <Search size={18} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Titre, lieu ou description..." />
          </div>
        </label>
        <label className="filter-field">
          <span>Type</span>
          <select value={type} onChange={(event) => setType(event.target.value)}>
            <option value="">Tous les types</option>
            {eventTypes.map((item) => <option value={item.value} key={item.value}>{item.label}</option>)}
          </select>
        </label>
        {(query || type) && (
          <button className="button button-secondary filter-reset" onClick={() => { setQuery(""); setType(""); }}>
            Reinitialiser
          </button>
        )}
      </div>

      <div className="student-event-grid">
        {filtered.map((event) => (
          <article className="student-event-card" key={event.id}>
            <div className="student-event-card-header">
              <span className="event-type-badge">{event.event_type_label}</span>
              <StatusBadge urgency={event.urgency}>{event.status}</StatusBadge>
            </div>
            <div className="student-event-card-body">
              <h2>{event.title}</h2>
              <p>{event.description}</p>
              <dl>
                <div>
                  <dt>Debut</dt>
                  <dd>{formatDate(event.start_date)}</dd>
                </div>
                {event.end_date !== event.start_date && (
                  <div>
                    <dt>Fin</dt>
                    <dd>{formatDate(event.end_date)}</dd>
                  </div>
                )}
                <div>
                  <dt>Lieu</dt>
                  <dd>{event.location || "Non precise"}</dd>
                </div>
              </dl>
            </div>
            <footer>
              <a className="button button-primary button-small" href={event.detail_url}>Voir le detail</a>
              <a className="button button-secondary button-small" href={event.calendar_url}>Ajouter agenda</a>
            </footer>
          </article>
        ))}
        {!filtered.length && (
          <div className="calendar-empty-state">
            <CalendarDays size={24} />
            <h2>Aucun evenement trouve</h2>
            <p>Modifiez la recherche ou le type selectionne.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function startOfMonth(value) {
  return new Date(value.getFullYear(), value.getMonth(), 1);
}

function addMonths(value, offset) {
  return new Date(value.getFullYear(), value.getMonth() + offset, 1);
}

function dateKey(value) {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function monthGrid(monthDate) {
  const first = startOfMonth(monthDate);
  const mondayOffset = (first.getDay() + 6) % 7;
  const gridStart = new Date(first);
  gridStart.setDate(first.getDate() - mondayOffset);
  return Array.from({ length: 42 }, (_, index) => {
    const day = new Date(gridStart);
    day.setDate(gridStart.getDate() + index);
    return day;
  });
}

function eventsForDay(events, day) {
  const key = dateKey(day);
  return events.filter((event) => event.start_date <= key && event.end_date >= key);
}

function AcademicMonthlyCalendar({ events, onNavigate }) {
  const [currentMonth, setCurrentMonth] = useState(startOfMonth(new Date()));
  const days = monthGrid(currentMonth);
  const monthStart = dateKey(startOfMonth(currentMonth));
  const nextMonthStart = dateKey(addMonths(currentMonth, 1));
  const monthEvents = events
    .filter((event) => event.start_date < nextMonthStart && event.end_date >= monthStart)
    .sort((first, second) => first.start_date.localeCompare(second.start_date));
  const monthLabel = new Intl.DateTimeFormat("fr-FR", { month: "long", year: "numeric" }).format(currentMonth);
  const todayKey = dateKey(new Date());
  const weekdays = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];

  return (
    <div className="page monthly-page">
      <PageHeader
        eyebrow="Calendrier academique"
        title={monthLabel}
        description={`${monthEvents.length} evenement(s) programme(s) ce mois-ci`}
        action={
          <div className="month-actions">
            <button className="button button-secondary" onClick={() => setCurrentMonth(addMonths(currentMonth, -1))}>
              <ChevronLeft size={17} /> Mois precedent
            </button>
            <button className="button button-secondary" onClick={() => onNavigate("calendar")}>Liste</button>
            <button className="button button-primary" onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}>
              Mois suivant <ChevronRight size={17} />
            </button>
          </div>
        }
      />

      <div className="monthly-layout">
        <section className="month-board">
          <div className="month-board-header">
            <div>
              <h2>Vue du mois</h2>
              <p>Les evenements sur plusieurs jours restent visibles chaque jour concerne.</p>
            </div>
            <div className="month-legend">
              <span><i className="legend-danger" /> Urgent</span>
              <span><i className="legend-warning" /> Proche</span>
              <span><i className="legend-success" /> En cours</span>
            </div>
          </div>
          <div className="month-weekdays">
            {weekdays.map((weekday) => <span key={weekday}>{weekday}</span>)}
          </div>
          <div className="month-grid">
            {days.map((day) => {
              const dayEvents = eventsForDay(events, day);
              const inMonth = day.getMonth() === currentMonth.getMonth();
              const key = dateKey(day);
              return (
                <div className={`month-day ${!inMonth ? "is-outside" : ""} ${key === todayKey ? "is-today" : ""}`} key={key}>
                  <div className="month-day-heading">
                    <strong>{day.getDate()}</strong>
                    {key === todayKey && <span>Aujourd'hui</span>}
                  </div>
                  <div className="month-day-events">
                    {dayEvents.slice(0, 3).map((event) => (
                      <a className={`month-event month-event-${event.urgency}`} href={event.detail_url} key={event.id}>
                        <strong>{event.title}</strong>
                        <small>{event.event_type_label}</small>
                      </a>
                    ))}
                    {inMonth && !dayEvents.length && <span className="month-free">Libre</span>}
                    {dayEvents.length > 3 && <span className="month-more">+{dayEvents.length - 3} autres</span>}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <aside className="month-planning">
          <header>
            <span>Planning</span>
            <strong>{monthEvents.length}</strong>
          </header>
          <div>
            {monthEvents.map((event) => (
              <a href={event.detail_url} key={event.id}>
                <span className="planning-date">{formatDate(event.start_date, { short: true })}</span>
                <div>
                  <strong>{event.title}</strong>
                  <small>{event.event_type_label} · {event.location || "Lieu non precise"}</small>
                </div>
              </a>
            ))}
            {!monthEvents.length && <EmptyInline text="Aucun evenement pour ce mois." />}
          </div>
        </aside>
      </div>
    </div>
  );
}

const chatSuggestions = [
  "Quelles sont les prochaines dates importantes ?",
  "Quand commencent les examens ?",
  "Quels evenements arrivent cette semaine ?",
];

function ChatExperience({ messages, setMessages, compact = false }) {
  const [question, setQuestion] = useState("");
  const [sending, setSending] = useState(false);

  async function submit(event) {
    event.preventDefault();
    if (!question.trim() || sending) return;
    const currentQuestion = question.trim();
    setQuestion("");
    setSending(true);
    try {
      const result = await api("/accounts/api/etudiant/chat/", {
        method: "POST",
        body: JSON.stringify({ question: currentQuestion }),
      });
      setMessages((items) => [...items, result.message]);
    } catch (requestError) {
      setQuestion(currentQuestion);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className={`chat-experience ${compact ? "is-compact" : ""}`}>
      <div className="conversation">
        {!messages.length && (
          <div className="assistant-empty">
            <span><Bot size={24} /></span>
            <h2>Que souhaitez-vous verifier ?</h2>
            <p>L'assistant utilise les evenements enregistres par l'administration.</p>
          </div>
        )}
        {messages.map((message) => (
          <div className="conversation-turn" key={message.id}>
            <div className="message message-user">
              <strong>Vous</strong>
              <p>{message.question}</p>
            </div>
            <div className="message message-assistant">
              <strong>AcadReminder</strong>
              <p>{message.answer}</p>
              <small className="message-meta">
                <span>{message.source_label || "Assistant"}</span>
                <span>{formatDateTime(message.created_at)}</span>
              </small>
            </div>
          </div>
        ))}
        {sending && <div className="typing">Recherche dans le calendrier...</div>}
      </div>
      <div className="assistant-suggestions">
        {chatSuggestions.map((item) => <button key={item} onClick={() => setQuestion(item)}>{item}</button>)}
      </div>
      <form className="assistant-composer" onSubmit={submit}>
        <input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Posez votre question..." />
        <button className="button button-primary" disabled={sending || !question.trim()}>Envoyer</button>
      </form>
    </div>
  );
}

function StudentAssistant({ messages, setMessages }) {
  return (
    <div className="page assistant-page">
      <PageHeader eyebrow="Assistant" title="Assistant academique" description="Interrogez directement les informations du calendrier." />
      <section className="assistant-panel">
        <ChatExperience messages={messages} setMessages={setMessages} />
      </section>
    </div>
  );
}

function ChatDrawer({ messages, setMessages, onClose, onExpand }) {
  return (
    <div className="chat-drawer-layer">
      <button className="chat-drawer-backdrop" onClick={onClose} aria-label="Fermer l'assistant" />
      <aside className="chat-drawer">
        <header>
          <div>
            <span className="chat-drawer-icon"><Bot size={19} /></span>
            <div>
              <strong>Assistant academique</strong>
              <small>Base sur votre calendrier</small>
            </div>
          </div>
          <div className="chat-drawer-actions">
            <button className="text-button" onClick={onExpand}>Agrandir</button>
            <button className="icon-button" onClick={onClose} aria-label="Fermer"><X size={19} /></button>
          </div>
        </header>
        <ChatExperience messages={messages} setMessages={setMessages} compact />
      </aside>
    </div>
  );
}

function StudentNotifications({ data, onRefresh }) {
  async function markAll() {
    await api("/accounts/api/etudiant/notifications/lues/", { method: "POST", body: "{}" });
    onRefresh();
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="Notifications"
        title="Centre de rappels"
        description="Les alertes generees selon vos preferences."
        action={
          <button className="button button-secondary" onClick={markAll} disabled={!data.summary.unread_notifications}>
            <Check size={17} /> Tout marquer comme lu
          </button>
        }
      />
      <section className="content-section">
        <div className="notification-list">
          {data.notifications.map((item) => (
            <article className={item.is_read ? "" : "is-unread"} key={item.id}>
              <span className="notification-icon"><Bell size={18} /></span>
              <div>
                <strong>{item.message}</strong>
                <p>{item.event.event_type_label} · {formatDate(item.event.start_date)}</p>
                <small>{formatDateTime(item.created_at)}</small>
              </div>
              {!item.is_read && <span className="unread-dot" />}
            </article>
          ))}
          {!data.notifications.length && <EmptyInline text="Aucune notification pour le moment." />}
        </div>
      </section>
    </div>
  );
}

function StudentPreferences({ data, onRefresh }) {
  const [types, setTypes] = useState(data.preference.event_types);
  const [days, setDays] = useState(data.preference.reminder_days);
  const [emailEnabled, setEmailEnabled] = useState(data.preference.email_enabled);
  const [saved, setSaved] = useState(false);

  function toggleType(value) {
    setTypes((items) => items.includes(value) ? items.filter((item) => item !== value) : [...items, value]);
  }

  async function save() {
    await api("/accounts/api/etudiant/preferences/", {
      method: "PUT",
      body: JSON.stringify({ event_types: types, reminder_days: Number(days), email_enabled: emailEnabled }),
    });
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2500);
    onRefresh();
  }

  return (
    <div className="page">
      <PageHeader eyebrow="Preferences" title="Mes rappels" description="Choisissez uniquement les alertes qui vous sont utiles." />
      <section className="settings-layout">
        <div className="settings-section">
          <h2>Types d'evenements suivis</h2>
          <p>Vous recevrez des rappels uniquement pour les categories selectionnees.</p>
          <div className="choice-grid">
            {data.event_types.map((item) => (
              <label key={item.value} className={types.includes(item.value) ? "is-selected" : ""}>
                <input type="checkbox" checked={types.includes(item.value)} onChange={() => toggleType(item.value)} />
                <span>{item.label}</span>
                <Check size={16} />
              </label>
            ))}
          </div>
        </div>
        <div className="settings-section">
          <h2>Delai et canal</h2>
          <label className="field">
            <span>Me prevenir</span>
            <select value={days} onChange={(event) => setDays(event.target.value)}>
              <option value="7">7 jours avant</option>
              <option value="3">3 jours avant</option>
              <option value="1">1 jour avant</option>
              <option value="0">Le jour meme</option>
            </select>
          </label>
          <label className="switch-row">
            <div>
              <strong>Rappels par email</strong>
              <small>Utiliser l'adresse associee a votre compte.</small>
            </div>
            <input type="checkbox" checked={emailEnabled} onChange={(event) => setEmailEnabled(event.target.checked)} />
          </label>
        </div>
        <div className="settings-actions">
          <button className="button button-primary" onClick={save}>{saved ? "Enregistre" : "Enregistrer"}</button>
        </div>
      </section>
    </div>
  );
}

function AcademicProfile({ user }) {
  const [form, setForm] = useState({
    first_name: user.first_name || "",
    last_name: user.last_name || "",
    email: user.email || "",
    role: user.role || "student",
    student_number: user.student_number || "",
    program: user.program || "",
    level: user.level || "",
    phone: user.phone || "",
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function save(event) {
    event.preventDefault();
    setSaving(true);
    setMessage("");
    setError("");
    try {
      await api("/accounts/api/profil/", {
        method: "PUT",
        body: JSON.stringify(form),
      });
      setMessage("Profil enregistre.");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="Compte academique"
        title="Mon profil"
        description="Maintenez vos informations afin que l'administration identifie correctement votre role."
      />
      <form className="profile-form" onSubmit={save}>
        <section>
          <div className="profile-section-heading">
            <h2>Identite</h2>
            <p>Informations principales de votre compte.</p>
          </div>
          <div className="profile-fields">
            <label className="field"><span>Prenom</span><input value={form.first_name} onChange={(event) => update("first_name", event.target.value)} /></label>
            <label className="field"><span>Nom</span><input value={form.last_name} onChange={(event) => update("last_name", event.target.value)} /></label>
            <label className="field profile-field-wide"><span>Email</span><input type="email" value={form.email} onChange={(event) => update("email", event.target.value)} required /></label>
          </div>
        </section>
        <section>
          <div className="profile-section-heading">
            <h2>Situation academique</h2>
            <p>Ces informations permettent de distinguer etudiants et enseignants.</p>
          </div>
          <div className="profile-fields">
            <label className="field">
              <span>Role</span>
              <select value={form.role} onChange={(event) => update("role", event.target.value)}>
                <option value="student">Etudiant</option>
                <option value="teacher">Enseignant</option>
              </select>
            </label>
            <label className="field"><span>Matricule ou identifiant</span><input value={form.student_number} onChange={(event) => update("student_number", event.target.value)} /></label>
            <label className="field"><span>Filiere ou departement</span><input value={form.program} onChange={(event) => update("program", event.target.value)} /></label>
            <label className="field"><span>Niveau ou fonction</span><input value={form.level} onChange={(event) => update("level", event.target.value)} /></label>
            <label className="field profile-field-wide"><span>Telephone</span><input value={form.phone} onChange={(event) => update("phone", event.target.value)} /></label>
          </div>
        </section>
        <footer>
          <div>
            {message && <span className="form-success">{message}</span>}
            {error && <span className="field-error">{error}</span>}
          </div>
          <button className="button button-primary" disabled={saving}>{saving ? "Enregistrement..." : "Enregistrer"}</button>
        </footer>
      </form>
    </div>
  );
}

const blankEvent = {
  title: "",
  description: "",
  event_type: "inscription",
  start_date: "",
  end_date: "",
  location: "",
};

function AdminApp({ user }) {
  const [view, setView] = useState("overview");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editor, setEditor] = useState(null);

  async function load() {
    try {
      setLoading(true);
      setData(await api("/accounts/api/admin/"));
      setError("");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const navigation = [
    { id: "overview", label: "Vue d'ensemble", icon: LayoutDashboard },
    { id: "events", label: "Evenements", icon: CalendarDays },
    { id: "users", label: "Utilisateurs", icon: Users },
  ];

  function openCreate() {
    setEditor({ mode: "create", event: blankEvent });
  }

  function openEdit(event) {
    setEditor({ mode: "edit", event });
  }

  return (
    <WorkspaceShell user={user} navigation={navigation} activeView={view} onNavigate={setView}>
      {loading && <LoadingState />}
      {error && <ErrorState message={error} onRetry={load} />}
      {data && view === "overview" && <AdminOverview data={data} onNavigate={setView} onCreate={openCreate} />}
      {data && view === "events" && <AdminEvents data={data} onCreate={openCreate} onEdit={openEdit} onRefresh={load} />}
      {data && view === "users" && <AdminUsers users={data.users} />}
      {editor && <EventEditor editor={editor} eventTypes={data.event_types} onClose={() => setEditor(null)} onSaved={load} />}
    </WorkspaceShell>
  );
}

function AdminOverview({ data, onNavigate, onCreate }) {
  return (
    <div className="page">
      <PageHeader
        eyebrow="Administration"
        title="Vue d'ensemble"
        description="L'etat du calendrier et des comptes en un coup d'oeil."
        action={<button className="button button-primary" onClick={onCreate}><Plus size={17} /> Nouvel evenement</button>}
      />
      <div className="metrics-grid metrics-grid-four">
        <Metric label="Utilisateurs" value={data.summary.users} detail="hors administrateurs" icon={Users} />
        <Metric label="Etudiants" value={data.summary.students} detail="comptes identifies" icon={CircleUserRound} />
        <Metric label="Enseignants" value={data.summary.teachers} detail="comptes identifies" icon={CircleUserRound} />
        <Metric label="Evenements" value={data.summary.events} detail="au calendrier" icon={CalendarDays} />
      </div>
      <div className="content-grid">
        <section className="content-section">
          <div className="section-heading">
            <div><h2>Prochains evenements</h2><p>Les premieres dates visibles par la communaute academique.</p></div>
            <button className="text-button" onClick={() => onNavigate("events")}>Gerer <ChevronRight size={16} /></button>
          </div>
          <div className="event-list">
            {data.events.slice(0, 6).map((event) => (
              <div className="event-row" key={event.id}>
                <div className="date-tile">
                  <strong>{new Date(`${event.start_date}T12:00:00`).getDate()}</strong>
                  <span>{formatDate(event.start_date, { short: true }).split(" ")[1]}</span>
                </div>
                <div className="event-row-main"><strong>{event.title}</strong><span>{event.event_type_label} · {event.location || "Lieu non precise"}</span></div>
                <StatusBadge urgency={event.urgency}>{event.status}</StatusBadge>
              </div>
            ))}
          </div>
        </section>
        <section className="content-section">
          <div className="section-heading"><div><h2>Comptes recents</h2><p>Derniers utilisateurs inscrits.</p></div></div>
          <div className="user-list">
            {data.users.slice(0, 5).map((account) => (
              <div key={account.id}>
                <span className="account-avatar">{account.name.slice(0, 2).toUpperCase()}</span>
                <div><strong>{account.name}</strong><small>{account.email || "Email non renseigne"}</small></div>
                <span className="role-label">{account.role}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

function AdminEvents({ data, onCreate, onEdit, onRefresh }) {
  const [query, setQuery] = useState("");
  const [type, setType] = useState("");
  const filtered = data.events.filter((event) => {
    const matches = `${event.title} ${event.description} ${event.location}`.toLowerCase().includes(query.toLowerCase());
    return matches && (!type || event.event_type === type);
  });

  async function remove(event) {
    if (!window.confirm(`Supprimer "${event.title}" ?`)) return;
    await api(`/accounts/api/admin/evenements/${event.id}/`, { method: "DELETE" });
    onRefresh();
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="Calendrier"
        title="Gestion des evenements"
        description="Creez et maintenez les informations utilisees par les etudiants et enseignants."
        action={<button className="button button-primary" onClick={onCreate}><Plus size={17} /> Ajouter</button>}
      />
      <div className="filter-bar">
        <label className="search-control"><Search size={18} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Rechercher..." /></label>
        <select value={type} onChange={(event) => setType(event.target.value)}>
          <option value="">Tous les types</option>
          {data.event_types.map((item) => <option value={item.value} key={item.value}>{item.label}</option>)}
        </select>
      </div>
      <section className="table-section">
        <div className="data-table">
          <div className="data-table-head">
            <span>Evenement</span><span>Periode</span><span>Lieu</span><span>Etat</span><span />
          </div>
          {filtered.map((event) => (
            <div className="data-table-row" key={event.id}>
              <div><strong>{event.title}</strong><small>{event.event_type_label}</small></div>
              <div><strong>{formatDate(event.start_date)}</strong><small>{event.end_date !== event.start_date ? `au ${formatDate(event.end_date)}` : "Une journee"}</small></div>
              <span>{event.location || "Non precise"}</span>
              <StatusBadge urgency={event.urgency}>{event.status}</StatusBadge>
              <div className="row-actions">
                <button className="icon-button" onClick={() => onEdit(event)} title="Modifier"><Pencil size={17} /></button>
                <button className="icon-button danger" onClick={() => remove(event)} title="Supprimer"><Trash2 size={17} /></button>
              </div>
            </div>
          ))}
          {!filtered.length && <EmptyInline text="Aucun evenement ne correspond a cette recherche." />}
        </div>
      </section>
    </div>
  );
}

function AdminUsers({ users }) {
  const [query, setQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const filteredUsers = users.filter((account) => {
    const matchesQuery = `${account.name} ${account.email} ${account.program}`.toLowerCase().includes(query.toLowerCase());
    return matchesQuery && (!roleFilter || account.role_value === roleFilter);
  });

  return (
    <div className="page">
      <PageHeader eyebrow="Utilisateurs" title="Comptes academiques" description="Identifiez les etudiants et enseignants inscrits sur la plateforme." />
      <div className="filter-bar">
        <label className="search-control">
          <Search size={18} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Nom, email, filiere ou departement..." />
        </label>
        <select value={roleFilter} onChange={(event) => setRoleFilter(event.target.value)}>
          <option value="">Tous les roles</option>
          <option value="student">Etudiants</option>
          <option value="teacher">Enseignants</option>
          <option value="admin">Administrateurs</option>
        </select>
      </div>
      <section className="table-section">
        <div className="data-table users-table">
          <div className="data-table-head"><span>Utilisateur</span><span>Email</span><span>Role</span><span>Inscription</span></div>
          {filteredUsers.map((account) => (
            <div className="data-table-row" key={account.id}>
              <div className="user-cell">
                <span className="account-avatar">{account.name.slice(0, 2).toUpperCase()}</span>
                <div>
                  <strong>{account.name}</strong>
                  {account.program && <small>{account.program}</small>}
                </div>
              </div>
              <span>{account.email || "Non renseigne"}</span>
              <span className="role-label">{account.role}</span>
              <span>{formatDateTime(account.date_joined)}</span>
            </div>
          ))}
          {!filteredUsers.length && <EmptyInline text="Aucun utilisateur ne correspond a ces filtres." />}
        </div>
      </section>
    </div>
  );
}

function EventEditor({ editor, eventTypes, onClose, onSaved }) {
  const [form, setForm] = useState({ ...editor.event });
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    setSaving(true);
    setErrors({});
    try {
      const url = editor.mode === "create"
        ? "/accounts/api/admin/evenements/"
        : `/accounts/api/admin/evenements/${editor.event.id}/`;
      await api(url, {
        method: editor.mode === "create" ? "POST" : "PUT",
        body: JSON.stringify(form),
      });
      await onSaved();
      onClose();
    } catch (requestError) {
      setErrors(requestError.data?.errors || { general: [{ message: requestError.message }] });
    } finally {
      setSaving(false);
    }
  }

  const errorFor = (field) => errors[field]?.[0]?.message;

  return (
    <div className="drawer-layer">
      <button className="drawer-backdrop" onClick={onClose} aria-label="Fermer" />
      <aside className="event-drawer">
        <header>
          <div><span>Calendrier</span><h2>{editor.mode === "create" ? "Nouvel evenement" : "Modifier l'evenement"}</h2></div>
          <button className="icon-button" onClick={onClose} aria-label="Fermer"><X size={20} /></button>
        </header>
        <form onSubmit={submit}>
          <div className="drawer-content">
            <label className="field"><span>Titre</span><input value={form.title} onChange={(event) => update("title", event.target.value)} required />{errorFor("title") && <small className="field-error">{errorFor("title")}</small>}</label>
            <label className="field"><span>Type</span><select value={form.event_type} onChange={(event) => update("event_type", event.target.value)}>{eventTypes.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
            <label className="field"><span>Description</span><textarea rows="5" value={form.description} onChange={(event) => update("description", event.target.value)} required />{errorFor("description") && <small className="field-error">{errorFor("description")}</small>}</label>
            <div className="field-row">
              <label className="field"><span>Date de debut</span><input type="date" value={form.start_date} onChange={(event) => update("start_date", event.target.value)} required />{errorFor("start_date") && <small className="field-error">{errorFor("start_date")}</small>}</label>
              <label className="field"><span>Date de fin</span><input type="date" value={form.end_date} onChange={(event) => update("end_date", event.target.value)} required />{errorFor("end_date") && <small className="field-error">{errorFor("end_date")}</small>}</label>
            </div>
            <label className="field"><span>Lieu</span><input value={form.location} onChange={(event) => update("location", event.target.value)} placeholder="Facultatif" />{errorFor("location") && <small className="field-error">{errorFor("location")}</small>}</label>
            {errors.general && <div className="form-error">{errors.general[0].message}</div>}
          </div>
          <footer>
            <button type="button" className="button button-secondary" onClick={onClose}>Annuler</button>
            <button className="button button-primary" disabled={saving}>{saving ? "Enregistrement..." : "Enregistrer"}</button>
          </footer>
        </form>
      </aside>
    </div>
  );
}

function LoadingState() {
  return <div className="state-page"><div className="loader" /><p>Chargement de votre espace...</p></div>;
}

function ErrorState({ message, onRetry }) {
  return <div className="state-page"><h2>Impossible de charger les donnees</h2><p>{message}</p><button className="button button-primary" onClick={onRetry}>Reessayer</button></div>;
}

function EmptyInline({ text }) {
  return <div className="empty-inline">{text}</div>;
}

function AuthApp({ initialMode = "login" }) {
  const [mode, setMode] = useState(initialMode);
  const [form, setForm] = useState({
    role: "student",
    username: "",
    first_name: "",
    last_name: "",
    email: "",
    student_number: "",
    program: "",
    level: "",
    phone: "",
    password: "",
    password1: "",
    password2: "",
  });
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    setSaving(true);
    setErrors({});
    try {
      const endpoint = mode === "login"
        ? "/accounts/api/auth/connexion/"
        : "/accounts/api/auth/inscription/";
      const payload = mode === "login"
        ? { username: form.username, password: form.password }
        : form;
      const result = await api(endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      window.location.href = result.user.is_staff
        ? "/accounts/espace-admin/"
        : "/accounts/espace-academique/";
    } catch (requestError) {
      setErrors(requestError.data?.errors || { general: [{ message: requestError.message }] });
    } finally {
      setSaving(false);
    }
  }

  const errorFor = (field) => errors[field]?.[0]?.message;

  return (
    <main className="auth-page">
      <section className="auth-intro">
        <a className="auth-brand" href="/">
          <span className="brand-mark">A</span>
          <strong>AcadReminder</strong>
        </a>
        <div>
          <span className="auth-eyebrow">Plateforme academique</span>
          <h1>Vos dates importantes, rappels et réponses au même endroit.</h1>
          <p>Consultez le calendrier académique et recevez les alertes utiles selon votre profil.</p>
        </div>
        <small>Django API + interface React</small>
      </section>

      <section className="auth-panel">
        <div className="auth-card">
          <div className="auth-tabs">
            <button className={mode === "login" ? "is-active" : ""} onClick={() => { setMode("login"); setErrors({}); }}>
              Connexion
            </button>
            <button className={mode === "register" ? "is-active" : ""} onClick={() => { setMode("register"); setErrors({}); }}>
              Inscription
            </button>
          </div>

          <header>
            <h2>{mode === "login" ? "Accéder à mon espace" : "Créer un compte académique"}</h2>
            <p>{mode === "login" ? "Utilisez vos identifiants pour continuer." : "Renseignez votre rôle et vos informations principales."}</p>
          </header>

          <form onSubmit={submit}>
            {mode === "register" && (
              <>
                <div className="auth-role-grid">
                  <button type="button" className={form.role === "student" ? "is-active" : ""} onClick={() => update("role", "student")}>
                    <strong>Étudiant</strong><span>Calendrier et rappels</span>
                  </button>
                  <button type="button" className={form.role === "teacher" ? "is-active" : ""} onClick={() => update("role", "teacher")}>
                    <strong>Enseignant</strong><span>Suivi académique</span>
                  </button>
                </div>
                <div className="auth-field-row">
                  <label className="field"><span>Prénom</span><input value={form.first_name} onChange={(event) => update("first_name", event.target.value)} required />{errorFor("first_name") && <small className="field-error">{errorFor("first_name")}</small>}</label>
                  <label className="field"><span>Nom</span><input value={form.last_name} onChange={(event) => update("last_name", event.target.value)} required />{errorFor("last_name") && <small className="field-error">{errorFor("last_name")}</small>}</label>
                </div>
                <label className="field"><span>Email</span><input type="email" value={form.email} onChange={(event) => update("email", event.target.value)} required />{errorFor("email") && <small className="field-error">{errorFor("email")}</small>}</label>
              </>
            )}

            <label className="field"><span>Nom d'utilisateur</span><input value={form.username} onChange={(event) => update("username", event.target.value)} autoComplete="username" required />{errorFor("username") && <small className="field-error">{errorFor("username")}</small>}</label>

            {mode === "login" ? (
              <label className="field"><span>Mot de passe</span><input type="password" value={form.password} onChange={(event) => update("password", event.target.value)} autoComplete="current-password" required /></label>
            ) : (
              <>
                <div className="auth-field-row">
                  <label className="field"><span>Matricule ou identifiant</span><input value={form.student_number} onChange={(event) => update("student_number", event.target.value)} /></label>
                  <label className="field"><span>Filière ou département</span><input value={form.program} onChange={(event) => update("program", event.target.value)} /></label>
                </div>
                <div className="auth-field-row">
                  <label className="field"><span>Niveau ou fonction</span><input value={form.level} onChange={(event) => update("level", event.target.value)} /></label>
                  <label className="field"><span>Téléphone</span><input value={form.phone} onChange={(event) => update("phone", event.target.value)} /></label>
                </div>
                <div className="auth-field-row">
                  <label className="field"><span>Mot de passe</span><input type="password" value={form.password1} onChange={(event) => update("password1", event.target.value)} autoComplete="new-password" required />{errorFor("password1") && <small className="field-error">{errorFor("password1")}</small>}</label>
                  <label className="field"><span>Confirmation</span><input type="password" value={form.password2} onChange={(event) => update("password2", event.target.value)} autoComplete="new-password" required />{errorFor("password2") && <small className="field-error">{errorFor("password2")}</small>}</label>
                </div>
              </>
            )}

            {errors.general && <div className="form-error">{errors.general[0].message}</div>}
            {errors.__all__ && <div className="form-error">{errors.__all__[0].message}</div>}
            <button className="button button-primary auth-submit" disabled={saving}>
              {saving ? "Traitement..." : mode === "login" ? "Se connecter" : "Créer mon compte"}
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}

function App() {
  const [session, setSession] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/accounts/api/session/")
      .then(setSession)
      .catch((requestError) => setError(requestError.message));
  }, []);

  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;
  if (!session) return <LoadingState />;
  if (!session.authenticated) {
    const registerPage = window.location.pathname.includes("inscription");
    return <AuthApp initialMode={registerPage ? "register" : "login"} />;
  }
  return session.user.is_staff ? <AdminApp user={session.user} /> : <StudentApp user={session.user} />;
}

createRoot(rootElement).render(<App />);
