import "./App.css";
import Status from "./Components/Status";

function App() {
  return (
    <div className="p-6 space-y-4">
      <div className="navbar bg-base-300">
        <a className="btn btn-ghost text-xl">GreyForm Operator GUI</a>
      </div>
      <div>
        <Status />
      </div>
    </div>
  );
}

export default App;
