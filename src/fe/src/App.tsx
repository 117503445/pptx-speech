import './App.css'
import { useState, useRef } from 'react';

function App() {
  const [isDisabled, setIsDisabled] = useState(false);

  const filePPTXRef = useRef<HTMLInputElement>(null);
  const filePDFRef = useRef<HTMLInputElement>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    console.log('submit');
    event.preventDefault();

    const target = event.target as HTMLFormElement;

    // TODO prevent empty
    const formData = new FormData(target);

    if (formData.get('file_pptx') == null) {
      alert('Please select pptx file');
      return;
    }
    let f: File = formData.get('file_pptx') as File;
    if (f.size == 0) {
      alert('Please select pptx file');
      return;
    }
    
    if (formData.get('file_pdf') == null) {
      alert('Please select pdf file');
      return;
    }
    f = formData.get('file_pdf') as File;
    if (f.size == 0) {
      alert('Please select pdf file');
      return;
    }




    setIsDisabled(true)

    const response = await fetch(import.meta.env.VITE_BE_HOST + '/api/task', {
      method: 'POST',
      body: formData
    });
    const data = await response.json();
    console.log(data);
    if (data['code'] != 0) {
      alert(data);
      setIsDisabled(false)
      return;
    }

    const taskID = data['data']['taskID'];
    const w = window.open('about:blank');
    if (w != null) {
      w.location.href = "/#/task/" + taskID;
    } else {
      alert('Please allow popups for this website');
    }

    if (filePPTXRef.current) {
      filePPTXRef.current.value = '';
    }

    if (filePDFRef.current) {
      filePDFRef.current.value = '';
    }

    setIsDisabled(false)
  }

  return (
    <>
      <h1>pptx-speech</h1>

      <p>朗读 PPTX 并生成视频</p>


      <form onSubmit={handleSubmit}>
        PPTX <input type="file" name="file_pptx" accept=".pptx" ref={filePPTXRef} />
        PDF <input type="file" name="file_pdf" accept=".pdf" ref={filePPTXRef} />
        <button type="submit" disabled={isDisabled}>提交</button>
      </form>

      <p>You can see more help on <a href='https://github.com/117503445/pptx-speech'>GitHub</a></p>
      <p>If it helps you, please give me a star :)</p>
    </>
  )
}

export default App
