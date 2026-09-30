/**
 * ShareAccessPage — public page at /share/:token for external recipients.
 *
 * Three views driven by share scope:
 *   DOCUMENT       — enter email → receive OTP → download or preview file
 *   CASE_DOCUMENTS — enter email → receive OTP → see list of docs → download or preview each
 *   CASE_FULL      — enter email → receive OTP → see case overview + members + docs
 *
 * allow_download=false hides/disables download; recipients can only preview via the
 * server-side PNG/text renderer. OCR formatted text rendered as markdown.
 * Preview supports fullscreen mode.
 *
 * Matches design/screens/ShareAccessPage.jsx (colours, spacing, structure).
 * No auth, no AppShell — fully self-contained.
 */

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import {
  Briefcase,
  CheckCircle2,
  Clock,
  Download,
  Expand,
  Eye,
  FileText,
  KeyRound,
  Mail,
  Shield,
  ShieldX,
  Shrink,
  Users,
  X,
} from "lucide-react";
import {
  getShareInfo,
  requestShareOtp,
  downloadShareDocument,
  accessCaseDocuments,
  accessCaseFull,
  downloadShareFile,
  previewShareDocument,
  previewShareFile,
} from "../lib/shareApi";
import type { SharePreview } from "../lib/shareApi";
import type { ShareInfo, SharedCaseDetail, SharedDocMeta } from "../types";

function fmtSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(1)} MB`;
}

function fmtExpiry(iso: string): string {
  try {
    const diff = new Date(iso).getTime() - Date.now();
    if (diff <= 0) return "Expired";
    const hours = Math.floor(diff / 3_600_000);
    const mins = Math.floor((diff % 3_600_000) / 60_000);
    if (hours > 0) return `Expires in ${hours}h ${mins}m`;
    return `Expires in ${mins} minutes`;
  } catch {
    return "";
  }
}

function triggerBlobDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 1000);
}

const OCR_LABEL: Record<string, string> = {
  NOT_APPLICABLE: "—",
  PENDING: "Processing",
  AWAITING_APPROVAL: "Pending review",
  DONE: "Verified",
  FAILED: "OCR failed",
};

const OCR_COLOR: Record<string, string> = {
  NOT_APPLICABLE: "#555869",
  PENDING: "#555869",
  AWAITING_APPROVAL: "#f59e0b",
  DONE: "#22c55e",
  FAILED: "#ef4444",
};

// ── OTP error → user-friendly message ────────────────────────────────────────────

function otpErrorMessage(code: string): string {
  switch (code) {
    case "EMAIL_MISMATCH": return "This link is not addressed to your email address.";
    case "OTP_REQUIRED": return "Please request an OTP first.";
    case "OTP_INVALID": return "Incorrect code — check your email and try again.";
    case "OTP_EXPIRED": return "The code has expired. Request a new one.";
    case "OTP_EXHAUSTED": return "Too many incorrect attempts. Request a new code.";
    case "EMAIL_UNAVAILABLE":
    case "EMAIL_SEND_FAILED": return "Failed to send OTP. Please try again or contact the link issuer.";
    case "RATE_LIMIT_EXCEEDED": return "Too many requests. Please wait before trying again.";
    default: return "Something went wrong. Please try again.";
  }
}

// ── Preview overlay ───────────────────────────────────────────────────────────────

interface PreviewOverlayProps {
  preview: SharePreview;
  filename: string;
  onClose: () => void;
}

function PreviewOverlay({ preview, filename, onClose }: PreviewOverlayProps) {
  const [fullscreen, setFullscreen] = useState(false);

  const containerStyle: React.CSSProperties = fullscreen
    ? { position: "fixed", inset: 0, zIndex: 200, background: "#0a0c10", overflowY: "auto", padding: "24px" }
    : { position: "fixed", inset: 0, zIndex: 200, background: "rgba(0,0,0,0.75)", display: "flex", alignItems: "flex-start", justifyContent: "center", padding: "32px 16px", overflowY: "auto" };

  const cardStyle: React.CSSProperties = fullscreen
    ? { maxWidth: 900, margin: "0 auto" }
    : { width: "720px", maxWidth: "100%", background: "#111318", border: "1px solid #2a2d35", borderRadius: "8px", overflow: "hidden" };

  return (
    <div style={containerStyle} onClick={fullscreen ? undefined : onClose}>
      <div style={cardStyle} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", padding: "14px 16px", borderBottom: "1px solid #2a2d35", background: "#1a1d24" }}>
          <FileText size={16} style={{ color: "#3b82f6", flexShrink: 0 }} />
          <span style={{ fontSize: "13px", color: "#e8eaf0", fontWeight: 500, flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {filename}
          </span>
          <button
            type="button"
            title={fullscreen ? "Exit fullscreen" : "Fullscreen"}
            onClick={() => setFullscreen(v => !v)}
            style={{ height: 28, width: 28, display: "flex", alignItems: "center", justifyContent: "center", background: "transparent", border: "none", borderRadius: 4, color: "#8b8fa8", cursor: "pointer" }}
          >
            {fullscreen ? <Shrink size={14} /> : <Expand size={14} />}
          </button>
          <button
            type="button"
            title="Close preview"
            onClick={onClose}
            style={{ height: 28, width: 28, display: "flex", alignItems: "center", justifyContent: "center", background: "transparent", border: "none", borderRadius: 4, color: "#8b8fa8", cursor: "pointer" }}
          >
            <X size={14} />
          </button>
        </div>

        <div style={{ padding: "16px" }}>
          {preview.mode === "text" && preview.text != null && (
            <div style={{ padding: "14px 18px", background: "#0a0c10", border: "1px solid #2a2d35", borderRadius: 6, fontSize: 13, color: "#e8eaf0", lineHeight: 1.75 }}>
              <ReactMarkdown>{preview.text}</ReactMarkdown>
            </div>
          )}

          {preview.mode === "pages" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {preview.pages_png_base64.map((b64, i) => (
                <img
                  key={i}
                  alt={`Page ${i + 1}`}
                  src={`data:image/png;base64,${b64}`}
                  style={{ width: "100%", borderRadius: 6, border: "1px solid #2a2d35", display: "block" }}
                />
              ))}
            </div>
          )}

          {preview.truncated && (
            <div style={{ marginTop: 10, fontSize: 11, color: "#555869" }}>
              Preview truncated — {preview.page_count} page{preview.page_count !== 1 ? "s" : ""} shown
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Root component ────────────────────────────────────────────────────────────────

export default function ShareAccessPage() {
  const { token } = useParams<{ token: string }>();
  const [info, setInfo] = useState<ShareInfo | null>(null);
  const [loading, setLoading] = useState(true);

  // Step 1: email
  const [email, setEmail] = useState("");
  const [otpLoading, setOtpLoading] = useState(false);
  const [otpSent, setOtpSent] = useState(false);

  // Step 2: OTP
  const [otp, setOtp] = useState("");

  const [error, setError] = useState("");
  const [accessed, setAccessed] = useState(false);
  const [docList, setDocList] = useState<SharedDocMeta[]>([]);
  const [caseDetail, setCaseDetail] = useState<SharedCaseDetail | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  // Preview state
  const [previewData, setPreviewData] = useState<SharePreview | null>(null);
  const [previewFilename, setPreviewFilename] = useState("");
  const [previewingId, setPreviewingId] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    void getShareInfo(token).then((i) => {
      setInfo(i);
      setLoading(false);
    }).catch(() => {
      setInfo({ scope: "DOCUMENT", filename: null, caseTitle: null, caseNumber: null, docCount: null, fileSizeBytes: null, expiresAt: "", requiresEmail: true, isValid: false, allowDownload: true });
      setLoading(false);
    });
  }, [token]);

  async function handleRequestOtp() {
    if (!token || !email) return;
    setError("");
    setOtpLoading(true);
    try {
      await requestShareOtp(token, email);
      setOtpSent(true);
      setOtp("");
    } catch (err) {
      setError(err instanceof Error ? otpErrorMessage(err.message) : otpErrorMessage(""));
    } finally {
      setOtpLoading(false);
    }
  }

  async function handleAccess() {
    if (!token || !info) return;
    setError("");

    if (info.scope === "DOCUMENT") {
      if (!info.allowDownload) {
        await handleDocumentPreview();
        return;
      }
      try {
        const blob = await downloadShareDocument(token, email, otp);
        triggerBlobDownload(blob, info.filename ?? "document");
        setDone(true);
      } catch (err) {
        const code = err instanceof Error ? err.message : "";
        if (code === "LINK_EXPIRED") {
          setInfo({ ...info, isValid: false });
        } else {
          setError(otpErrorMessage(code));
          if (code === "OTP_EXHAUSTED" || code === "OTP_EXPIRED") {
            setOtpSent(false);
            setOtp("");
          }
        }
      }
      return;
    }

    if (info.scope === "CASE_DOCUMENTS") {
      try {
        const { documents } = await accessCaseDocuments(token, email, otp);
        setDocList(documents);
        setAccessed(true);
      } catch (err) {
        const code = err instanceof Error ? err.message : "";
        if (code === "LINK_EXPIRED") {
          setInfo({ ...info, isValid: false });
        } else {
          setError(otpErrorMessage(code));
          if (code === "OTP_EXHAUSTED" || code === "OTP_EXPIRED") {
            setOtpSent(false);
            setOtp("");
          }
        }
      }
      return;
    }

    // CASE_FULL
    try {
      const result = await accessCaseFull(token, email, otp);
      setCaseDetail(result.case);
      setDocList(result.documents);
      setAccessed(true);
    } catch (err) {
      const code = err instanceof Error ? err.message : "";
      if (code === "LINK_EXPIRED") {
        setInfo({ ...info, isValid: false });
      } else {
        setError(otpErrorMessage(code));
        if (code === "OTP_EXHAUSTED" || code === "OTP_EXPIRED") {
          setOtpSent(false);
          setOtp("");
        }
      }
    }
  }

  async function handleDocumentPreview() {
    if (!token || !info) return;
    setError("");
    setPreviewingId("__doc__");
    try {
      const data = await previewShareDocument(token, email || null, otp);
      setPreviewFilename(info.filename ?? "Document");
      setPreviewData(data);
    } catch (err) {
      const code = err instanceof Error ? err.message : "";
      if (code === "LINK_EXPIRED") {
        if (info) setInfo({ ...info, isValid: false });
      } else {
        setError(otpErrorMessage(code));
        if (code === "OTP_EXHAUSTED" || code === "OTP_EXPIRED") {
          setOtpSent(false);
          setOtp("");
        }
      }
    } finally {
      setPreviewingId(null);
    }
  }

  async function handleFileDownload(doc: SharedDocMeta) {
    if (!token) return;
    setDownloadingId(doc.id);
    setError("");
    try {
      const { blob, filename } = await downloadShareFile(token, doc.id, email, otp);
      triggerBlobDownload(blob, filename);
    } catch (err) {
      const code = err instanceof Error ? err.message : "";
      setError(code === "LINK_EXPIRED" ? "The share link has expired." : `Download failed for ${doc.filename}.`);
    } finally {
      setDownloadingId(null);
    }
  }

  async function handleFilePreview(doc: SharedDocMeta) {
    if (!token) return;
    setPreviewingId(doc.id);
    setError("");
    try {
      const data = await previewShareFile(token, doc.id, email || null, otp);
      setPreviewFilename(doc.filename);
      setPreviewData(data);
    } catch (err) {
      const code = err instanceof Error ? err.message : "";
      setError(code === "LINK_EXPIRED" ? "The share link has expired." : `Preview failed for ${doc.filename}.`);
    } finally {
      setPreviewingId(null);
    }
  }

  // ── Loading ───────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <PageShell>
        <div style={{ color: "#8b8fa8", fontSize: "14px" }}>Loading…</div>
      </PageShell>
    );
  }

  // ── Dead / expired ────────────────────────────────────────────────────────────

  if (!info || !info.isValid) {
    return (
      <PageShell>
        <div style={{
          width: "420px", maxWidth: "100%",
          background: "#111318", border: "1px solid #2a2d35", borderRadius: "8px",
          padding: "28px 24px", display: "flex", flexDirection: "column",
          alignItems: "center", gap: "12px", textAlign: "center",
        }}>
          <div style={{ color: "#ef4444" }}><ShieldX size={36} /></div>
          <div style={{ fontSize: "17px", fontWeight: 600, color: "#e8eaf0" }}>
            This link is no longer valid.
          </div>
          <div style={{ fontSize: "13px", color: "#8b8fa8", lineHeight: 1.6, maxWidth: "300px" }}>
            It may have expired, been revoked, or reached its maximum number of uses.
          </div>
          <div style={{ fontSize: "13px", color: "#8b8fa8" }}>
            Contact the issuing officer for a new link.
          </div>
        </div>
      </PageShell>
    );
  }

  const allowDownload = info.allowDownload;

  // ── Case accessed view ────────────────────────────────────────────────────────

  if (accessed) {
    return (
      <PageShell>
        {previewData && (
          <PreviewOverlay
            preview={previewData}
            filename={previewFilename}
            onClose={() => setPreviewData(null)}
          />
        )}
        <div style={{
          width: "680px", maxWidth: "100%",
          background: "#111318", border: "1px solid #2a2d35", borderRadius: "8px",
          padding: "24px", display: "flex", flexDirection: "column", gap: "20px",
        }}>
          {/* Case detail (CASE_FULL only) */}
          {caseDetail && (
            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div style={{ display: "flex", gap: "12px", alignItems: "flex-start" }}>
                <div style={{ color: "#3b82f6", marginTop: "2px" }}><Briefcase size={20} /></div>
                <div>
                  <div style={{ fontSize: "16px", fontWeight: 600, color: "#e8eaf0" }}>{caseDetail.title}</div>
                  <div style={{ fontSize: "12px", color: "#8b8fa8", fontFamily: "'JetBrains Mono', monospace", marginTop: "2px" }}>{caseDetail.caseNumber}</div>
                  {caseDetail.description && (
                    <div style={{ fontSize: "13px", color: "#8b8fa8", marginTop: "8px", lineHeight: 1.5 }}>{caseDetail.description}</div>
                  )}
                  <div style={{ display: "flex", gap: "12px", marginTop: "8px", flexWrap: "wrap" }}>
                    <span style={{ fontSize: "12px", color: "#8b8fa8" }}>Status: <span style={{ color: "#e8eaf0" }}>{caseDetail.status}</span></span>
                    <span style={{ fontSize: "12px", color: "#8b8fa8" }}>Priority: <span style={{ color: "#e8eaf0" }}>{caseDetail.priority}</span></span>
                  </div>
                </div>
              </div>

              <div style={{ background: "#1a1d24", border: "1px solid #2a2d35", borderRadius: "6px", padding: "12px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
                  <Users size={14} style={{ color: "#8b8fa8" }} />
                  <span style={{ fontSize: "13px", fontWeight: 500, color: "#e8eaf0" }}>Case Members ({caseDetail.memberCount})</span>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                  {caseDetail.members.map((m, i) => (
                    <div key={i} style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                      <span style={{ color: "#e8eaf0" }}>{m.fullName}</span>
                      <span style={{ color: "#8b8fa8" }}>{m.role}{m.department ? ` · ${m.department}` : ""}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Document list */}
          <div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
              <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8eaf0" }}>
                Documents ({docList.length})
              </div>
              {!allowDownload && (
                <span style={{ fontSize: "11px", color: "#f59e0b", padding: "2px 8px", background: "#3d2c08", border: "1px solid #f59e0b", borderRadius: 4 }}>
                  View only — download disabled
                </span>
              )}
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {docList.map((doc) => (
                <div key={doc.id} style={{ display: "flex", flexDirection: "column", gap: 0 }}>
                  <div style={{
                    background: "#1a1d24", border: "1px solid #2a2d35", borderRadius: "6px",
                    padding: "12px", display: "flex", alignItems: "center", gap: "12px",
                  }}>
                    <FileText size={16} style={{ color: "#3b82f6", flexShrink: 0 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: "13px", fontWeight: 500, color: "#e8eaf0", wordBreak: "break-all" }}>{doc.filename}</div>
                      <div style={{ display: "flex", gap: "10px", marginTop: "4px", flexWrap: "wrap" }}>
                        <span style={{ fontSize: "11px", color: "#8b8fa8" }}>{doc.docType.replace(/_/g, " ")}</span>
                        <span style={{ fontSize: "11px", color: "#8b8fa8" }}>{fmtSize(doc.fileSizeBytes)}</span>
                        {doc.ocrStatus !== "NOT_APPLICABLE" && (
                          <span style={{ fontSize: "11px", color: OCR_COLOR[doc.ocrStatus] ?? "#555869" }}>
                            OCR: {OCR_LABEL[doc.ocrStatus] ?? doc.ocrStatus}
                            {doc.ocrStatus === "DONE" && doc.ocrConfidence != null ? ` (${Math.round(doc.ocrConfidence * 100)}%)` : ""}
                          </span>
                        )}
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                      <button
                        type="button"
                        onClick={() => void handleFilePreview(doc)}
                        disabled={previewingId === doc.id}
                        style={{
                          height: "30px", padding: "0 10px",
                          display: "flex", alignItems: "center", gap: "5px",
                          background: "#1e2028", border: "1px solid #2a2d35", borderRadius: "4px",
                          color: "#8b8fa8", fontSize: "12px", cursor: previewingId === doc.id ? "not-allowed" : "pointer",
                        }}
                      >
                        <Eye size={12} />
                        {previewingId === doc.id ? "…" : "View"}
                      </button>
                      {allowDownload && (
                        <button
                          type="button"
                          onClick={() => void handleFileDownload(doc)}
                          disabled={downloadingId === doc.id}
                          style={{
                            height: "30px", padding: "0 10px",
                            display: "flex", alignItems: "center", gap: "5px",
                            background: downloadingId === doc.id ? "#1e3a5f" : "#3b82f6",
                            color: "#fff", border: "none", borderRadius: "4px",
                            fontSize: "12px", cursor: downloadingId === doc.id ? "not-allowed" : "pointer",
                          }}
                        >
                          <Download size={12} />
                          {downloadingId === doc.id ? "…" : "Download"}
                        </button>
                      )}
                    </div>
                  </div>

                  {doc.ocrStatus === "DONE" && doc.ocrFormattedText && (
                    <div style={{
                      marginTop: 4, padding: "12px 16px",
                      background: "#0a0c10", border: "1px solid #2a2d35",
                      borderTop: "none", borderRadius: "0 0 6px 6px",
                      fontSize: 12, color: "#e8eaf0", lineHeight: 1.75,
                    }}>
                      <div style={{ fontSize: 10, letterSpacing: "0.06em", color: "#555869", fontFamily: "JetBrains Mono, monospace", marginBottom: 8 }}>
                        OCR TEXT (FORMATTED)
                      </div>
                      <ReactMarkdown>{doc.ocrFormattedText}</ReactMarkdown>
                    </div>
                  )}
                </div>
              ))}
              {docList.length === 0 && (
                <div style={{ fontSize: "13px", color: "#555869", padding: "12px 0" }}>No documents in this case.</div>
              )}
            </div>
          </div>

          {error && (
            <div style={{ background: "#3d1010", border: "1px solid #ef4444", borderRadius: "6px", padding: "9px 11px", fontSize: "12px", color: "#ef4444" }}>
              {error}
            </div>
          )}

          <footer style={{ fontSize: "11px", color: "#555869", textAlign: "center", display: "flex", alignItems: "center", justifyContent: "center", gap: "6px" }}>
            <Shield size={12} /> All access is logged and audited.
          </footer>
        </div>
      </PageShell>
    );
  }

  // ── Initial access form ───────────────────────────────────────────────────────

  const isDocScope = info.scope === "DOCUMENT";
  const viewOnly = isDocScope && !allowDownload;
  const canSubmit = otp.length === 6 && !previewingId;

  return (
    <PageShell>
      {previewData && (
        <PreviewOverlay
          preview={previewData}
          filename={previewFilename}
          onClose={() => setPreviewData(null)}
        />
      )}
      <div style={{
        width: "420px", maxWidth: "100%",
        background: "#111318", border: "1px solid #2a2d35", borderRadius: "8px",
        padding: "24px", display: "flex", flexDirection: "column", gap: "18px",
      }}>
        {/* Document / case header */}
        <div style={{ display: "flex", gap: "12px", alignItems: "flex-start" }}>
          <div style={{ color: "#3b82f6", marginTop: "2px" }}>
            {isDocScope ? <FileText size={20} /> : <Briefcase size={20} />}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "4px", minWidth: 0 }}>
            {isDocScope ? (
              <>
                <div style={{ fontSize: "15px", fontWeight: 600, color: "#e8eaf0", wordBreak: "break-all" }}>
                  {info.filename ?? "Document"}
                </div>
                <div style={{ fontSize: "12px", color: "#8b8fa8" }}>
                  {info.fileSizeBytes != null ? fmtSize(info.fileSizeBytes) : ""}
                </div>
                {viewOnly && (
                  <div style={{ fontSize: "11px", color: "#f59e0b", padding: "2px 6px", background: "#3d2c08", border: "1px solid #f59e0b", borderRadius: 4, alignSelf: "flex-start", marginTop: 2 }}>
                    View only — download disabled
                  </div>
                )}
              </>
            ) : (
              <>
                <div style={{ fontSize: "15px", fontWeight: 600, color: "#e8eaf0" }}>
                  {info.caseTitle ?? "Case"}
                </div>
                <div style={{ fontSize: "12px", color: "#8b8fa8", fontFamily: "'JetBrains Mono', monospace" }}>
                  {info.caseNumber ?? ""}
                </div>
                <div style={{ fontSize: "12px", color: "#8b8fa8", marginTop: "2px" }}>
                  {info.scope === "CASE_FULL" ? "Full case view" : "All case documents"} · {info.docCount ?? 0} document{info.docCount !== 1 ? "s" : ""}
                </div>
                {!allowDownload && (
                  <div style={{ fontSize: "11px", color: "#f59e0b", padding: "2px 6px", background: "#3d2c08", border: "1px solid #f59e0b", borderRadius: 4, alignSelf: "flex-start", marginTop: 2 }}>
                    View only — download disabled
                  </div>
                )}
              </>
            )}
            {info.expiresAt && (
              <div style={{ fontSize: "12px", color: "#f59e0b", display: "flex", alignItems: "center", gap: "6px", marginTop: "2px" }}>
                <Clock size={14} /> {fmtExpiry(info.expiresAt)}
              </div>
            )}
          </div>
        </div>

        {/* Step 1 — email */}
        <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
          <label htmlFor="sh-email" style={{ fontSize: "13px", fontWeight: 500, color: "#e8eaf0" }}>
            {info.requiresEmail
              ? "Email address this link was sent to"
              : "Your email address"}
          </label>
          <div style={{ display: "flex", gap: "8px" }}>
            <input
              id="sh-email"
              type="email"
              placeholder="Enter your email"
              value={email}
              disabled={otpLoading}
              onChange={(e) => {
                setEmail(e.target.value);
                setOtpSent(false);
                setOtp("");
                setError("");
              }}
              onKeyDown={(e) => { if (e.key === "Enter" && email && !otpSent) void handleRequestOtp(); }}
              style={{
                flex: 1, height: "36px", padding: "0 10px", fontSize: "14px",
                color: "#e8eaf0", background: "#1e2028",
                border: "1px solid #2a2d35", borderRadius: "6px",
              }}
            />
            <button
              type="button"
              onClick={() => void handleRequestOtp()}
              disabled={!email || otpLoading}
              style={{
                height: "36px", padding: "0 14px", flexShrink: 0,
                display: "flex", alignItems: "center", gap: "6px",
                background: otpSent ? "#1a2a1a" : "#3b82f6",
                color: otpSent ? "#22c55e" : "#fff",
                border: otpSent ? "1px solid #22c55e" : "none",
                borderRadius: "6px", fontSize: "13px", fontWeight: 500,
                cursor: !email || otpLoading ? "not-allowed" : "pointer",
                opacity: !email || otpLoading ? 0.6 : 1,
              }}
            >
              <Mail size={14} />
              {otpLoading ? "Sending…" : otpSent ? "Resend" : "Send OTP"}
            </button>
          </div>
          {otpSent && (
            <div style={{ fontSize: "12px", color: "#22c55e", display: "flex", alignItems: "center", gap: "6px" }}>
              <CheckCircle2 size={13} /> Code sent to {email} — valid for 10 minutes
            </div>
          )}
        </div>

        {/* Step 2 — OTP input (shown after code is sent) */}
        {otpSent && (
          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            <label htmlFor="sh-otp" style={{ fontSize: "13px", fontWeight: 500, color: "#e8eaf0", display: "flex", alignItems: "center", gap: "6px" }}>
              <KeyRound size={13} style={{ color: "#8b8fa8" }} /> 6-digit access code
            </label>
            <input
              id="sh-otp"
              type="text"
              inputMode="numeric"
              maxLength={6}
              placeholder="000000"
              value={otp}
              onChange={(e) => { setOtp(e.target.value.replace(/\D/g, "").slice(0, 6)); setError(""); }}
              onKeyDown={(e) => { if (e.key === "Enter" && canSubmit) void handleAccess(); }}
              style={{
                height: "44px", padding: "0 14px", fontSize: "22px",
                letterSpacing: "0.3em", textAlign: "center",
                color: "#e8eaf0", background: "#1e2028",
                border: `1px solid ${otp.length === 6 ? "#3b82f6" : "#2a2d35"}`,
                borderRadius: "6px", fontFamily: "'JetBrains Mono', monospace",
              }}
              autoFocus
            />
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{ background: "#3d1010", border: "1px solid #ef4444", borderRadius: "6px", padding: "9px 11px", fontSize: "12px", color: "#ef4444" }}>
            {error}
          </div>
        )}

        {/* Action button — only shown after OTP sent */}
        {otpSent && (
          <button
            type="button"
            onClick={() => void handleAccess()}
            disabled={!canSubmit}
            style={{
              height: "34px", display: "flex", alignItems: "center", justifyContent: "center",
              gap: "8px", background: canSubmit ? "#3b82f6" : "#1e2028",
              color: canSubmit ? "#ffffff" : "#555869",
              border: canSubmit ? "none" : "1px solid #2a2d35",
              borderRadius: "4px", fontSize: "14px", fontWeight: 500,
              cursor: canSubmit ? "pointer" : "not-allowed",
            }}
          >
            {isDocScope
              ? viewOnly
                ? <><Eye size={16} /> {previewingId === "__doc__" ? "Loading preview…" : "View Document"}</>
                : <><Download size={16} /> Download Document</>
              : <><Briefcase size={16} /> Access {info.scope === "CASE_FULL" ? "Full Case" : "Documents"}</>}
          </button>
        )}

        {/* Success banner (document scope download) */}
        {done && (
          <div style={{
            display: "flex", gap: "8px", alignItems: "center",
            background: "#14391f", border: "1px solid #22c55e",
            borderRadius: "6px", padding: "10px 12px",
            fontSize: "13px", color: "#e8eaf0",
          }}>
            <CheckCircle2 size={16} /> Download started. This access has been logged.
          </div>
        )}

        <footer style={{ fontSize: "11px", color: "#555869", textAlign: "center", display: "flex", alignItems: "center", justifyContent: "center", gap: "6px" }}>
          <Shield size={14} /> Accessed links are logged and audited.
        </footer>
      </div>
    </PageShell>
  );
}

// ── Layout shell ──────────────────────────────────────────────────────────────────

function PageShell({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      minHeight: "100vh", display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      gap: "28px", padding: "48px 24px",
      background: "#0a0c10", color: "#e8eaf0",
    }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "10px" }}>
        <div style={{ color: "#3b82f6" }}><Shield size={36} /></div>
        <div style={{ fontSize: "24px", fontWeight: 700, letterSpacing: "0.18em", color: "#e8eaf0" }}>PRAMAAN</div>
        <div style={{ fontSize: "13px", color: "#8b8fa8" }}>Secure Evidence Vault</div>
      </div>
      {children}
    </div>
  );
}
