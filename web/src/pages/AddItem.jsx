
import { useState } from "react";

import {
  Alert,
  Box,
  Button,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import api from "../services/api";

const initialForm = {
  sku: "",
  name: "",
  category: "",
  item_type: "RENTAL",
  price: "",
  total_units: "1",
  weight_g: "",
  tags: "",
};

function AddItem() {
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState("");
  const [apiError, setApiError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));

    setErrors((previous) => ({
      ...previous,
      [name]: "",
    }));

    setSuccess("");
    setApiError("");
  }

  function validateForm() {
    const newErrors = {};

    if (!/^\d{10}$/.test(form.sku)) {
      newErrors.sku = "SKU must contain exactly 10 digits.";
    }

    if (!form.name.trim()) {
      newErrors.name = "Equipment name is required.";
    }

    if (!form.category.trim()) {
      newErrors.category = "Category is required.";
    }

    if (
      form.price === "" ||
      !Number.isFinite(Number(form.price)) ||
      Number(form.price) <= 0
    ) {
      newErrors.price = "Price must be greater than zero.";
    }

    if (
      form.total_units === "" ||
      !Number.isInteger(Number(form.total_units)) ||
      Number(form.total_units) < 1
    ) {
      newErrors.total_units =
        "Units must be a whole number of at least 1.";
    }

    if (
      form.weight_g !== "" &&
      (
        !Number.isInteger(Number(form.weight_g)) ||
        Number(form.weight_g) < 0
      )
    ) {
      newErrors.weight_g =
        "Weight must be a non-negative whole number.";
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setSuccess("");
    setApiError("");

    if (!validateForm()) {
      return;
    }

    setSubmitting(true);

    try {
      const payload = {
        sku: form.sku.trim(),
        name: form.name.trim(),
        category: form.category.trim(),
        item_type:
          form.item_type === "DISPLAY" ? "Display" : "Equipment",
        price: Number(form.price),
        total_units: Number(form.total_units),
        weight_g: form.weight_g === "" ? 0 : Number(form.weight_g),
        tags: form.tags
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean),
      };

      const response = await api.post("/gear", payload);

      setSuccess(
        `${response.data.item.name} was added successfully!`
      );

      setForm(initialForm);
      setErrors({});
    } catch (error) {
      const message =
        error.response?.data?.message ||
        error.response?.data?.detail?.message ||
        error.message ||
        "Something went wrong while adding equipment.";

      setApiError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight="bold">
          Add Equipment
        </Typography>

        <Typography color="text.secondary">
          Register new equipment in the GearShare catalogue.
        </Typography>
      </Box>

      <Paper
        elevation={0}
        sx={{
          p: { xs: 2, sm: 4 },
          borderRadius: 3,
          border: "1px solid #e0e7ef",
        }}
      >
        <Box component="form" onSubmit={handleSubmit}>
          <Stack spacing={2.5}>
            <TextField
              label="SKU"
              name="sku"
              value={form.sku}
              onChange={handleChange}
              error={Boolean(errors.sku)}
              helperText={errors.sku || "Enter exactly 10 digits."}
              required
              fullWidth
              inputProps={{ maxLength: 10, inputMode: "numeric" }}
            />

            <TextField
              label="Equipment Name"
              name="name"
              value={form.name}
              onChange={handleChange}
              error={Boolean(errors.name)}
              helperText={errors.name}
              required
              fullWidth
            />

            <TextField
              label="Category"
              name="category"
              value={form.category}
              onChange={handleChange}
              error={Boolean(errors.category)}
              helperText={errors.category}
              required
              fullWidth
            />

            <TextField
              select
              label="Item Type"
              name="item_type"
              value={form.item_type}
              onChange={handleChange}
              fullWidth
            >
              <MenuItem value="RENTAL">Rental Equipment</MenuItem>
              <MenuItem value="DISPLAY">Display Only</MenuItem>
            </TextField>

            <TextField
              label="Replacement Price (₹)"
              name="price"
              type="number"
              value={form.price}
              onChange={handleChange}
              error={Boolean(errors.price)}
              helperText={errors.price}
              required
              fullWidth
              inputProps={{ min: 0.01, step: "0.01" }}
            />

            <TextField
              label="Total Units"
              name="total_units"
              type="number"
              value={form.total_units}
              onChange={handleChange}
              error={Boolean(errors.total_units)}
              helperText={errors.total_units}
              required
              fullWidth
              inputProps={{ min: 1, step: 1 }}
            />

            <TextField
              label="Weight (grams)"
              name="weight_g"
              type="number"
              value={form.weight_g}
              onChange={handleChange}
              error={Boolean(errors.weight_g)}
              helperText={errors.weight_g || "Optional"}
              fullWidth
              inputProps={{ min: 0, step: 1 }}
            />

            <TextField
              label="Tags"
              name="tags"
              value={form.tags}
              onChange={handleChange}
              helperText="Optional. Separate multiple tags with commas."
              fullWidth
            />

            {success && (
              <Alert severity="success" role="status">
                {success}
              </Alert>
            )}

            {apiError && (
              <Alert severity="error" role="alert">
                {apiError}
              </Alert>
            )}

            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={submitting}
              fullWidth
            >
              {submitting ? "Adding Equipment..." : "Add Equipment"}
            </Button>
          </Stack>
        </Box>
      </Paper>
    </Stack>
  );
}

export default AddItem;
