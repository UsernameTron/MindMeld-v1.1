import React, { useState } from 'react';

const Calculator = () => {
  const [a, setA] = useState(0);
  const [b, setB] = useState(0);
  const [result, setResult] = useState(0);
  const [operation, setOperation] = useState('add');

  const calculate = () => {
    if (operation === 'add') {
      setResult(Number(a) + Number(b));
    } else if (operation === 'subtract') {
      setResult(Number(a) - Number(b));
    }
  };

  return (
    <div className="calculator">
      <h2>Simple Calculator</h2>
      <div>
        <input
          type="number"
          value={a}
          onChange={(e) => setA(e.target.value)}
          aria-label="First number"
        />
        <select
          value={operation}
          onChange={(e) => setOperation(e.target.value)}
          aria-label="Operation"
        >
          <option value="add">+</option>
          <option value="subtract">-</option>
        </select>
        <input
          type="number"
          value={b}
          onChange={(e) => setB(e.target.value)}
          aria-label="Second number"
        />
        <button onClick={calculate}>=</button>
        <span data-testid="result">{result}</span>
      </div>
    </div>
  );
};

export default Calculator;
