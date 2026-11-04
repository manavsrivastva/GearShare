
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Select,
  MenuItem,
  FormControl,
  Badge,
} from "@mui/material";

import { Link } from "react-router-dom";
import { useCustomer } from "../context/CustomerContext";
import { useBasket } from "../context/BasketContext";

const customers = [
  { id: "C001", name: "Ananya Nair" },
  { id: "C002", name: "Vikram Shah" },
  { id: "C003", name: "Meera Joshi" },
  { id: "C004", name: "Rohan Das" },
  { id: "C005", name: "Pooja Menon" },
];

function Navbar() {
  const { customer, setCustomer } = useCustomer();
  const { basketCount } = useBasket();

  const handleCustomerChange = (event) => {
    const selected = customers.find(
      (c) => c.id === event.target.value
    );

    setCustomer(selected || null);
  };

  return (
    <AppBar position="static">
      <Toolbar sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          GearShare
        </Typography>

        <Button color="inherit" component={Link} to="/">
          Catalogue
        </Button>

        <Button color="inherit" component={Link} to="/me">
          My Rentals
        </Button>

        <Button color="inherit" component={Link} to="/basket">
          <Badge badgeContent={basketCount} color="error">
            Basket
          </Badge>
        </Button>

        <Button color="inherit" component={Link} to="/admin/add">
          Add Item
        </Button>

        <FormControl
          size="small"
          sx={{
            minWidth: 170,
            bgcolor: "white",
            borderRadius: 1,
          }}
        >
          <Select
            value={customer?.id || ""}
            onChange={handleCustomerChange}
            displayEmpty
          >
            <MenuItem value="" disabled>
              Select Customer
            </MenuItem>

            {customers.map((c) => (
              <MenuItem key={c.id} value={c.id}>
                {c.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
