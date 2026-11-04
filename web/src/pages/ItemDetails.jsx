
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Paper,
  Stack,
  Typography,
  Divider,
  Chip,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import api from "../services/api";
import AvailabilityBadge from "../components/AvailabilityBadge";
import { useCustomer } from "../context/CustomerContext";
import { useBasket } from "../context/BasketContext";

function ItemDetails() {
  const { sku } = useParams();
  const { customer } = useCustomer();
  const { items, addItem } = useBasket();

  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [renting, setRenting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [notice, setNotice] = useState("");
  const [basketMessage, setBasketMessage] = useState("");

  const alreadyAdded = item
    ? items.some((basketItem) => basketItem.sku === item.sku)
    : false;

  useEffect(() => {
    const controller = new AbortController();

    async function fetchItem() {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(`/gear/${sku}`, {
          signal: controller.signal,
        });

        setItem(response.data);
      } catch (err) {
        if (err.code !== "ERR_CANCELED") {
          const detail = err.response?.data?.detail;
          setError(
            detail?.message ||
            err.response?.data?.message ||
            "Unable to load item details."
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    fetchItem();

    return () => controller.abort();
  }, [sku]);

  function handleAddToBasket() {
    setBasketMessage("");

    if (!item.can_be_rented) {
      setBasketMessage("Display-only items cannot be added to the basket.");
      return;
    }

    if (alreadyAdded) {
      setBasketMessage("This item is already in your basket.");
      return;
    }

    addItem(item);
    setBasketMessage(`${item.name} added to your basket successfully.`);
  }

  async function handleRent() {
    setError("");
    setSuccess("");
    setNotice("");

    if (!customer) {
      setError("Please select a customer from the navigation bar first.");
      return;
    }

    if (!item.can_be_rented) {
      setError("This display-only item cannot be rented.");
      return;
    }

    try {
      setRenting(true);

      const response = await api.post("/rentals", {
        customer_id: customer.id,
        sku: item.sku,
      });

      setSuccess(
        `Rental created successfully! Rental ID: ${response.data.rental_id}. Due date: ${response.data.due_date}.`
      );

      setItem((previous) => ({
        ...previous,
        available_units: Math.max(0, previous.available_units - 1),
      }));
    } catch (err) {
      const detail = err.response?.data?.detail;
      const errorCode = detail?.error;
      const message =
        detail?.message ||
        err.response?.data?.message ||
        "Unable to process your request.";

      if (errorCode === "ItemUnavailableError") {
        setNotice(message);
        setItem((previous) => ({
          ...previous,
          available_units: 0,
        }));
      } else {
        setError(message);
      }
    } finally {
      setRenting(false);
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 5 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error && !item) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!item) {
    return <Alert severity="warning">Item not found.</Alert>;
  }

  const canBeRented = item.can_be_rented;
  const isAvailable = item.available_units > 0;

  return (
    <Stack spacing={3}>
      <Button
        component={Link}
        to="/"
        startIcon={<ArrowBackIcon />}
        sx={{ alignSelf: "flex-start" }}
      >
        Back to Catalogue
      </Button>

      <Paper
        elevation={0}
        sx={{
          p: { xs: 3, md: 4 },
          borderRadius: 3,
          border: "1px solid #e0e7ef",
        }}
      >
        <Stack spacing={2}>
          <Box>
            <Typography variant="overline" color="text.secondary">
              {item.category}
            </Typography>

            <Typography variant="h4" fontWeight="bold">
              {item.name}
            </Typography>

            <Typography color="text.secondary">
              SKU: {item.sku}
            </Typography>
          </Box>

          <Divider />

          <Typography>
            <strong>Item type:</strong> {item.item_type}
          </Typography>

          <Typography>
            <strong>Replacement price:</strong> ₹{item.price}
          </Typography>

          <Typography>
            <strong>Total units:</strong> {item.total_units}
          </Typography>

          <Typography>
            <strong>Available units:</strong> {item.available_units}
          </Typography>

          {item.weight_g != null && (
            <Typography>
              <strong>Weight:</strong> {item.weight_g} g
            </Typography>
          )}

          {Array.isArray(item.tags) && item.tags.length > 0 && (
            <Box>
              <Typography fontWeight="bold" gutterBottom>
                Tags
              </Typography>

              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {item.tags.map((tag) => (
                  <Chip key={tag} label={tag} size="small" />
                ))}
              </Stack>
            </Box>
          )}

          <Divider />

          {canBeRented ? (
            <AvailabilityBadge available={item.available_units} />
          ) : (
            <Chip label="Display only" color="default" />
          )}

          {!canBeRented && (
            <Alert severity="info">
              This item is for display purposes only and cannot be rented.
            </Alert>
          )}

          {canBeRented && !isAvailable && (
            <Alert severity="warning">
              This item is currently out of stock. You can join its waiting list.
            </Alert>
          )}

          {customer ? (
            <Typography variant="body2" color="text.secondary">
              Selected customer: <strong>{customer.name}</strong> ({customer.id})
            </Typography>
          ) : (
            <Alert severity="info">
              Select a customer from the navigation bar before continuing.
            </Alert>
          )}

          {error && <Alert severity="error">{error}</Alert>}
          {success && <Alert severity="success">{success}</Alert>}
          {notice && <Alert severity="success">{notice}</Alert>}
          {basketMessage && (
            <Alert severity="info">{basketMessage}</Alert>
          )}

          <Button
            variant="outlined"
            size="large"
            onClick={handleAddToBasket}
            disabled={!canBeRented || alreadyAdded}
          >
            {!canBeRented
              ? "Display Only"
              : alreadyAdded
                ? "Already in Basket"
                : "Add to Basket"}
          </Button>

          <Button
            variant="contained"
            size="large"
            onClick={handleRent}
            disabled={renting || !canBeRented || !customer}
          >
            {renting
              ? "Processing..."
              : !canBeRented
                ? "Display Only"
                : isAvailable
                  ? "Rent This Item"
                  : "Join Waiting List"}
          </Button>
        </Stack>
      </Paper>
    </Stack>
  );
}

export default ItemDetails;
