import { useEffect, useState } from "react";
import { api } from "../api";

const PAGE_SIZE = 5;

export default function Orders() {
  const [page, setPage] = useState(0);
  const [data, setData] = useState({ items: [], total: 0 });
  const [error, setError] = useState("");

  useEffect(() => {
    api(`/orders?limit=${PAGE_SIZE}&offset=${page * PAGE_SIZE}`)
      .then(setData)
      .catch((e) => setError(e.message));
  }, [page]);

  const lastPage = Math.max(0, Math.ceil(data.total / PAGE_SIZE) - 1);

  return (
    <div className="box">
      <h2>My orders</h2>
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr><th>Order</th><th>Status</th><th>Total</th><th>Est. delivery</th></tr>
        </thead>
        <tbody>
          {data.items.map((o) => (
            <tr key={o.id}>
              <td>#{o.order_number}</td>
              <td>{o.status}</td>
              <td>{o.total_amount}</td>
              <td>{o.estimated_delivery ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="pager">
        <button className="ghost" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
        <span className="muted">Page {page + 1} of {lastPage + 1}</span>
        <button className="ghost" disabled={page >= lastPage} onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </div>
  );
}