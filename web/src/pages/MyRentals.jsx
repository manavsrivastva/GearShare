
import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  CircularProgress,
  Paper,
  Stack,
  Typography,
  Chip,
} from "@mui/material";

import api from "../services/api";
import { useCustomer } from "../context/CustomerContext";

function MyRentals() {
  const { customer } = useCustomer();

  const [rentals, setRentals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [returningId, setReturningId] = useState(null);

  async function fetchRentals(signal) {
    if (!customer) return;

    try {
      setLoading(true);
      setError("");

      const response = await api.get(
        `/customers/${customer.id}/rentals`,
        { signal }
      );

      const data = response.data;

      setRentals(
  Array.isArray(data) ? data : data.active || []
);
    } catch (err) {
      if (err.code !== "ERR_CANCELED") {
        setError(
          err.response?.data?.message ||
          "Unable to load rentals."
        );
      }
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  }

  useEffect(() => {
    if (!customer) {
      setRentals([]);
      return;
    }

    const controller = new AbortController();

    fetchRentals(controller.signal);

    return () => controller.abort();
  }, [customer]);

  async function handleReturn(rentalId) {
    try {
      setReturningId(rentalId);
      setError("");
      setSuccess("");

      await api.post(`/rentals/${rentalId}/return`);

      setSuccess(
        `Rental ${rentalId} returned successfully.`
      );

      await fetchRentals();
    } catch (err) {
      setError(
        err.response?.data?.message ||
        "Unable to return this item."
      );
    } finally {
      setReturningId(null);
    }
  }

  if (!customer) {
    return (
      <Alert severity="info">
        Please select a customer from the Navbar to view rentals.
      </Alert>
    );
  }

  return (
    <Stack spacing={3}>
      <Typography variant="h4" fontWeight="bold">
        My Rentals
      </Typography>

      <Typography color="text.secondary">
        Customer: {customer.name} ({customer.id})
      </Typography>

      {success && (
        <Alert severity="success">{success}</Alert>
      )}

      {error && (
        <Alert severity="error">{error}</Alert>
      )}

      {loading && <CircularProgress />}

      {!loading && !error && rentals.length === 0 && (
        <Alert severity="info">
          No rentals found for this customer.
        </Alert>
      )}

      {!loading && rentals.map((rental) => (
        <Paper
          key={rental.rental_id}
          sx={{ p: 3, borderRadius: 2 }}
        >
          <Stack spacing={1}>
            <Typography variant="h6" fontWeight="bold">
              Rental ID: {rental.rental_id}
            </Typography>

            <Typography>
  Item: {rental.item}
</Typography>

<Typography>
  Rental ID: {rental.rental_id}
</Typography>

<Typography>
  Due Date: {rental.due_date}
</Typography>

<Typography>
  Days Overdue: {rental.days_overdue}
</Typography>

<Chip
  label="Active"
  color="warning"
  sx={{ alignSelf: "flex-start" }}
/>

            {!rental.return_date && (
              <Button
                variant="contained"
                color="success"
                disabled={returningId === rental.rental_id}
                onClick={() => handleReturn(rental.rental_id)}
                sx={{ alignSelf: "flex-start" }}
              >
                {returningId === rental.rental_id
                  ? "Returning..."
                  : "Return Item"}
              </Button>
            )}
          </Stack>
        </Paper>
      ))}
    </Stack>
  );
}

export default MyRentals;
