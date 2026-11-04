
import { useState } from "react";
import {
  Alert,
  Box,
  Button,
  Divider,
  Paper,
  Stack,
  Typography,
  CircularProgress,
} from "@mui/material";

import { Link } from "react-router-dom";
import { useBasket } from "../context/BasketContext";
import { useCustomer } from "../context/CustomerContext";
import api from "../services/api";

function Basket() {
  const {
    items,
    removeItem,
    clearBasket,
    basketCount,
    totalReplacementValue,
  } = useBasket();

  const { customer } = useCustomer();

  const [checkingOut, setCheckingOut] = useState(false);
  const [checkoutResults, setCheckoutResults] = useState([]);
  const [checkoutError, setCheckoutError] = useState("");

  async function handleCheckout() {
    setCheckoutError("");
    setCheckoutResults([]);

    if (!customer) {
      setCheckoutError(
        "Please select a customer from the navigation bar before checkout."
      );
      return;
    }

    if (items.length === 0) {
      setCheckoutError("Your basket is empty.");
      return;
    }

    setCheckingOut(true);

    const results = [];
    const successfulSkus = [];

    for (const item of items) {
      try {
        const response = await api.post("/rentals", {
          customer_id: customer.id,
          sku: item.sku,
        });

        successfulSkus.push(item.sku);

        results.push({
          sku: item.sku,
          name: item.name,
          success: true,
          message: `Rental ID: ${response.data.rental_id}. Due date: ${response.data.due_date}.`,
        });
      } catch (err) {
        const detail = err.response?.data?.detail;

        results.push({
          sku: item.sku,
          name: item.name,
          success: false,
          message:
            detail?.message ||
            err.response?.data?.message ||
            "Unable to create rental.",
        });
      }
    }

    successfulSkus.forEach((sku) => removeItem(sku));

    setCheckoutResults(results);
    setCheckingOut(false);
  }

  if (items.length === 0 && checkoutResults.length === 0) {
    return (
      <Stack spacing={3}>
        <Typography variant="h4" fontWeight="bold">
          Your Basket
        </Typography>

        <Paper sx={{ p: 4, textAlign: "center", borderRadius: 3 }}>
          <Typography variant="h6">
            Your basket is empty
          </Typography>

          <Typography color="text.secondary" sx={{ mt: 1 }}>
            Browse the catalogue and add equipment to your basket.
          </Typography>

          <Button
            component={Link}
            to="/"
            variant="contained"
            sx={{ mt: 3 }}
          >
            Browse Catalogue
          </Button>
        </Paper>
      </Stack>
    );
  }

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight="bold">
          Your Basket
        </Typography>

        <Typography color="text.secondary">
          {basketCount} item(s) selected
        </Typography>
      </Box>

      {customer ? (
        <Alert severity="info">
          Checking out as {customer.name} ({customer.id})
        </Alert>
      ) : (
        <Alert severity="warning">
          Please select a customer from the navigation bar before checkout.
        </Alert>
      )}

      {checkoutError && (
        <Alert severity="error">{checkoutError}</Alert>
      )}

      {checkoutResults.length > 0 && (
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h6" fontWeight="bold" gutterBottom>
            Checkout Results
          </Typography>

          <Stack spacing={2}>
            {checkoutResults.map((result) => (
              <Alert
                key={result.sku}
                severity={result.success ? "success" : "error"}
              >
                <strong>{result.name}</strong>
                <br />
                {result.message}
              </Alert>
            ))}
          </Stack>
        </Paper>
      )}

      {items.length > 0 && (
        <>
          <Alert severity="info">
            Adding equipment to your basket does not create a rental.
            Rentals are created only after checkout is confirmed by the server.
          </Alert>

          <Stack spacing={2}>
            {items.map((item) => (
              <Paper
                key={item.sku}
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 3,
                  border: "1px solid #e0e7ef",
                }}
              >
                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  justifyContent="space-between"
                  spacing={2}
                >
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      {item.name}
                    </Typography>

                    <Typography variant="body2" color="text.secondary">
                      SKU: {item.sku}
                    </Typography>

                    <Typography variant="body2">
                      Category: {item.category}
                    </Typography>

                    <Typography fontWeight="bold" sx={{ mt: 1 }}>
                      Replacement Price: ₹{item.price}
                    </Typography>
                  </Box>

                  <Button
                    color="error"
                    disabled={checkingOut}
                    onClick={() => removeItem(item.sku)}
                    sx={{
                      alignSelf: { xs: "flex-start", sm: "center" },
                    }}
                  >
                    Remove
                  </Button>
                </Stack>
              </Paper>
            ))}
          </Stack>

          <Paper
            elevation={0}
            sx={{
              p: 3,
              borderRadius: 3,
              border: "1px solid #e0e7ef",
            }}
          >
            <Stack spacing={2}>
              <Typography variant="h6" fontWeight="bold">
                Basket Summary
              </Typography>

              <Divider />

              <Stack direction="row" justifyContent="space-between">
                <Typography>Total Items</Typography>
                <Typography fontWeight="bold">{basketCount}</Typography>
              </Stack>

              <Stack direction="row" justifyContent="space-between">
                <Typography>Total Replacement Value</Typography>
                <Typography fontWeight="bold">
                  ₹{totalReplacementValue.toLocaleString("en-IN")}
                </Typography>
              </Stack>

              <Divider />

              <Button
                component={Link}
                to="/"
                variant="outlined"
                disabled={checkingOut}
                fullWidth
              >
                Continue Browsing
              </Button>

              <Button
                color="error"
                variant="outlined"
                disabled={checkingOut}
                onClick={clearBasket}
                fullWidth
              >
                Clear Basket
              </Button>

              <Button
                variant="contained"
                fullWidth
                size="large"
                disabled={checkingOut || !customer || items.length === 0}
                onClick={handleCheckout}
              >
                {checkingOut ? (
                  <>
                    <CircularProgress
                      size={20}
                      color="inherit"
                      sx={{ mr: 1 }}
                    />
                    Processing Checkout...
                  </>
                ) : (
                  "Checkout & Rent Equipment"
                )}
              </Button>
            </Stack>
          </Paper>
        </>
      )}
    </Stack>
  );
}

export default Basket;
