import React, { useEffect, useState } from "react";
import type { JSX } from "react";

/**
 * Minimal component:
 * - Let the user set a "default folder" (stored in IndexedDB).
 * - "Select file" opens the file picker with startIn set to that default folder when available.
 * - After picking, the UI shows only the selected file name.
 *
 * Notes:
 * - Browsers do NOT allow arbitrary filesystem paths for security. You can only
 *   use well-known locations (e.g. "documents") or a previously-stored directory handle.
 * - This component stores the directory handle in IndexedDB using structured cloning.
 * - showOpenFilePicker/showDirectoryPicker require a secure context (https or localhost).
 */

const IDB_DB_NAME = "fs-handles";
const IDB_STORE_NAME = "handles";
const IDB_KEY = "defaultDir";

type SelectedFile = {
  name: string;
  size?: number;
  type?: string;
  url?: string;
};

export default function SelectPBU(): JSX.Element {
  const [savedDirHandle, setSavedDirHandle] = useState<any | null>(null);
  const [selected, setSelected] = useState<SelectedFile | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // load saved handle on mount
    (async () => {
      try {
        const h = await getSavedDirectoryHandle();
        if (h) {
          // try to request/query permission; if user has already granted it, great.
          const ok = await ensureReadPermission(h);
          if (ok) setSavedDirHandle(h);
        }
      } catch (err) {
        console.error("Failed to load saved directory handle:", err);
      }
    })();

    return () => {
      // cleanup blob url if any
      if (selected?.url) URL.revokeObjectURL(selected.url);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ----- IndexedDB helpers to persist a FileSystemDirectoryHandle -----
  function openDB(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(IDB_DB_NAME, 1);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(IDB_STORE_NAME)) {
          db.createObjectStore(IDB_STORE_NAME);
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async function saveDirectoryHandle(handle: any): Promise<void> {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(IDB_STORE_NAME, "readwrite");
      tx.objectStore(IDB_STORE_NAME).put(handle, IDB_KEY);
      tx.oncomplete = () => {
        db.close();
        resolve();
      };
      tx.onerror = () => {
        db.close();
        reject(tx.error);
      };
    });
  }

  async function getSavedDirectoryHandle(): Promise<any | null> {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(IDB_STORE_NAME, "readonly");
      const req = tx.objectStore(IDB_STORE_NAME).get(IDB_KEY);
      req.onsuccess = () => {
        db.close();
        resolve(req.result ?? null);
      };
      req.onerror = () => {
        db.close();
        reject(req.error);
      };
    });
  }

  // ----- permission helpers -----
  async function ensureReadPermission(handle: any): Promise<boolean> {
    if (!handle) return false;
    try {
      // queryPermission / requestPermission are optional on some implementations
      if (handle.queryPermission) {
        const q = await handle.queryPermission({ mode: "read" });
        if (q === "granted") return true;
      }
      if (handle.requestPermission) {
        const r = await handle.requestPermission({ mode: "read" });
        return r === "granted";
      }
      // If neither is present, assume it's usable (older/blink implementations may behave differently)
      return true;
    } catch (err) {
      console.warn("Permission check failed:", err);
      return false;
    }
  }

  // ----- UI actions -----
  async function handleSetDefaultFolder() {
    setLoading(true);
    try {
      const dirHandle = await (window as any).showDirectoryPicker();
      const ok = await ensureReadPermission(dirHandle);
      if (!ok) {
        console.warn("User did not grant permission to the chosen folder.");
        setSavedDirHandle(null);
        return;
      }
      await saveDirectoryHandle(dirHandle);
      setSavedDirHandle(dirHandle);
    } catch (err: any) {
      // user likely cancelled; ignore
      console.error("Set default folder cancelled/failed:", err?.message ?? err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSelectFile() {
    setLoading(true);
    try {
      // startIn accepts either a well-known string or a previously-obtained handle
      // If savedDirHandle exists we use it; otherwise fall back to "documents".
      const startIn = savedDirHandle ?? "documents";
      // showOpenFilePicker returns an array of file handles
      const fileHandles = await (window as any).showOpenFilePicker({
        startIn,
        multiple: false,
      });
      if (!fileHandles || fileHandles.length === 0) return;
      const fileHandle = fileHandles[0];
      const file = await fileHandle.getFile();
      // cleanup old URL
      if (selected?.url) URL.revokeObjectURL(selected.url);
      const url = URL.createObjectURL(file);
      setSelected({ name: file.name, size: file.size, type: file.type, url });
    } catch (err: any) {
      // user may cancel the picker; ignore silently
      console.error("File pick cancelled/failed:", err?.message ?? err);
    } finally {
      setLoading(false);
    }
  }

  function handleClearSelection() {
    if (selected?.url) URL.revokeObjectURL(selected.url);
    setSelected(null);
  }

  return (
    <div>
      <div className="flex gap-2 justify-between">
        {/*
        <button
          className="btn btn-sm btn-outline"
          onClick={handleSetDefaultFolder}
          type="button"
          disabled={loading}
          title="Set a default folder that will be used as the starting folder for the file picker"
        >
          {savedDirHandle ? "Change default folder" : "Set default folder"}
        </button>
        */}
        {(!selected) && (
        <button
          className="btn btn-primary md:btn-md lg:btn-lg w-1/2 py-2 px-4 border-b-4 border-blue-700 hover:border-gray-700 rounded"
          onClick={handleSelectFile}
          type="button"
          disabled={loading}
        >
          {loading ? "Opening…" : "Select file"}
        </button>
        )}

        {selected && (
        <>
          <button
            className="btn btn-primary md:btn-md lg:btn-lg w-1/2 py-2 px-4 border-b-4 border-blue-700 hover:border-gray-700 rounded"
            onClick={handleSelectFile}
            type="button"
            disabled={loading}
          >
            {loading ? "Opening…" : "Next"}
          </button>

          <button
          className="btn btn-warning md:btn-md lg:btn-lg py-2 px-4 rounded border-b-4
                      border-yellow-700 hover:border-gray-700
                      disabled:border-gray-300 disabled:cursor-not-allowed disabled:opacity-0 disabled:hover:border-gray-300"
          onClick={handleClearSelection}
          type="button"
          disabled={loading || !selected}
          >
          Clear selection
          </button>
        </>
        )}

      </div>
    
      <div className="mt-3 flex gap-2 items-center">
        <div className="menu bg-base-200 rounded-box w-full p-3 text-black">
          {selected ? (
            <div>
              <div className="font-medium">Selected file</div>
              <div className="truncate" title={selected.name}>
                {selected.name}
              </div>
            </div>
          ) : (
            <div>No file selected.</div>
          )}
        </div>
      </div>
    </div>
  );
}