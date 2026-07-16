import React, { useState, useCallback, useRef } from "react";
import { api } from "../api";

export default function UploadPanel({ onUploaded }) {
  const [dragActive, setDragActive] = useState(false);
  const [status, setStatus] = useState(null); // { type: 'success'|'error'|'loading', message }
  const inputRef = useRef(null);

  const handleFiles = useCallback(
    async (fileList) => {
      const files = Array.from(fileList);
      if (files.length === 0) return;

      setStatus({ type: "loading", message: `Processing ${files.length} file(s)...` });

      let successCount = 0;
      let lastError = null;

      for (const file of files) {
        try {
          await api.uploadDocument(file);
          successCount += 1;
        } catch (err) {
          lastError = err.message;
        }
      }

      if (lastError && successCount === 0) {
        setStatus({ type: "error", message: `Upload failed: ${lastError}` });
      } else if (lastError) {
        setStatus({
          type: "error",
          message: `Processed ${successCount}/${files.length}. Last error: ${lastError}`,
        });
      } else {
        setStatus({
          type: "success",
          message: `Extracted and analyzed ${successCount} document(s).`,
        });
      }
      onUploaded();
    },
    [onUploaded]
  );

  const onDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div className="upload-panel">
      <h2>Upload documents</h2>
      <div
        className={`dropzone ${dragActive ? "drag-active" : ""}`}
        onClick={() => inputRef.current.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={onDrop}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".png,.jpg,.jpeg,.pdf,.txt,.csv"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <div>
          <strong>Click to upload</strong> or drag invoices, expense claims, or ledger
          files here
          <br />
          Supports PNG, JPG, PDF, TXT — processed with OCR and cross-checked against
          existing records
        </div>
      </div>
      {status && (
        <div className={`upload-status ${status.type === "error" ? "error" : status.type === "success" ? "success" : ""}`}>
          {status.message}
        </div>
      )}
    </div>
  );
}
