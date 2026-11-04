
import { useEffect, useMemo, useState } from "react";
import {
  Typography,
  Paper,
  TextField,
  CircularProgress,
  Alert,
  Stack,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
  Button,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import ClearIcon from "@mui/icons-material/Clear";

import api from "../services/api";
import GearList from "../components/GearList";

function Home() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [sort, setSort] = useState("name");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Fetch equipment whenever the search term changes.
  useEffect(() => {
    const controller = new AbortController();

    async function fetchGear() {
      try {
        setLoading(true);
        setError("");

        const response = await api.get("/gear", {
          params: { q: search },
          signal: controller.signal,
        });

        setItems(response.data);
      } catch (err) {
        if (err.code !== "ERR_CANCELED") {
          setError(
            err.response?.data?.message ||
              "Unable to load equipment. Please try again."
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    const timer = setTimeout(fetchGear, 300);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [search]);

  // Build category options from the equipment returned by the API.
  const categories = useMemo(() => {
    return [
      "All",
      ...new Set(items.map((item) => item.category).filter(Boolean)),
    ];
  }, [items]);

  // Apply category filtering and sorting.
  const displayedItems = useMemo(() => {
    let result = [...items];

    if (category !== "All") {
      result = result.filter((item) => item.category === category);
    }

    switch (sort) {
      case "name":
        result.sort((a, b) => a.name.localeCompare(b.name));
        break;

      case "price_low":
        result.sort((a, b) => a.price - b.price);
        break;

      case "price_high":
        result.sort((a, b) => b.price - a.price);
        break;

      case "availability":
        result.sort((a, b) => b.available_units - a.available_units);
        break;

      default:
        break;
    }

    return result;
  }, [items, category, sort]);

  function clearFilters() {
    setSearch("");
    setCategory("All");
    setSort("name");
  }

  return (
    <Stack spacing={3}>
      {/* Page heading */}
      <Paper
        elevation={0}
        sx={{
          p: { xs: 3, md: 4 },
          borderRadius: 3,
          background: "linear-gradient(135deg, #e3f2fd, #ffffff)",
          border: "1px solid #e0e7ef",
        }}
      >
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          GearShare Catalogue
        </Typography>

        <Typography color="text.secondary">
          Discover equipment, explore categories and find what you need.
        </Typography>
      </Paper>

      {/* Search and filters */}
      <Paper elevation={0} sx={{ p: 3, borderRadius: 3, border: "1px solid #e0e7ef" }}>
        <Stack spacing={2}>
          <TextField
            fullWidth
            label="Search equipment"
            placeholder="Search by item name or SKU"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: search && (
                <InputAdornment position="end">
                  <Button
                    size="small"
                    onClick={() => setSearch("")}
                    aria-label="Clear search"
                  >
                    <ClearIcon />
                  </Button>
                </InputAdornment>
              ),
            }}
          />

          <Box
            sx={{
              display: "flex",
              gap: 2,
              flexWrap: "wrap",
            }}
          >
            <FormControl sx={{ flex: 1, minWidth: 180 }}>
              <InputLabel id="category-label">Category</InputLabel>
              <Select
                labelId="category-label"
                value={category}
                label="Category"
                onChange={(event) => setCategory(event.target.value)}
              >
                {categories.map((value) => (
                  <MenuItem key={value} value={value}>
                    {value}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl sx={{ flex: 1, minWidth: 180 }}>
              <InputLabel id="sort-label">Sort by</InputLabel>
              <Select
                labelId="sort-label"
                value={sort}
                label="Sort by"
                onChange={(event) => setSort(event.target.value)}
              >
                <MenuItem value="name">Name: A to Z</MenuItem>
                <MenuItem value="price_low">Price: Low to High</MenuItem>
                <MenuItem value="price_high">Price: High to Low</MenuItem>
                <MenuItem value="availability">Availability</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="body2" color="text.secondary">
              {loading
                ? "Loading equipment..."
                : `${displayedItems.length} item(s) found`}
            </Typography>

            <Button onClick={clearFilters} color="inherit" size="small">
              Clear filters
            </Button>
          </Box>
        </Stack>
      </Paper>

      {/* Equipment results */}
      <Typography variant="h5" fontWeight="bold">
        Equipment
      </Typography>

      {loading && (
        <Box display="flex" justifyContent="center" py={5}>
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error">{error}</Alert>}

      {!loading && !error && <GearList items={displayedItems} />}
    </Stack>
  );
}

export default Home;
