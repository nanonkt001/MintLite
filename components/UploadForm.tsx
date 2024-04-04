import { useState } from "react";
export function UploadForm(){
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  return (
    <form style={{display:"grid", gap:12}}>
      <input placeholder="Name" value={name} onChange={e=>setName(e.target.value)} />
      <textarea placeholder="Description" value={description} onChange={e=>setDescription(e.target.value)} />
      <button type="button">Prepare Metadata</button>
    </form>
  );
}
