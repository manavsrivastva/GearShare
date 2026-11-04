
import {
  Card,
  CardContent,
  Typography,
  Button,
  Stack,
} from "@mui/material";

import { Link } from "react-router-dom";
import AvailabilityBadge from "./AvailabilityBadge";
import { useBasket } from "../context/BasketContext";

function GearCard({ item }) {
  const { items, addItem } = useBasket();

  const alreadyAdded = items.some(
    (basketItem) => basketItem.sku === item.sku
  );

  const handleAddToBasket = () => {
    addItem(item);
  };

  return (
    <Card
      sx={{
        height: "100%",
        borderRadius: 3,
        transition: "0.2s",
        "&:hover": {
          transform: "translateY(-4px)",
          boxShadow: 5,
        },
      }}
    >
      <CardContent>
        <Stack spacing={1.5}>
          <Typography variant="h6" fontWeight="bold">
            {item.name}
          </Typography>

          <Typography color="text.secondary" variant="body2">
            SKU: {item.sku}
          </Typography>

          <Typography variant="body2">
            Category: {item.category}
          </Typography>

          <Typography variant="body2">
            Type: {item.item_type}
          </Typography>

          <Typography variant="body1" fontWeight="bold">
            Replacement Price: ₹{item.price}
          </Typography>

          <AvailabilityBadge available={item.available_units} />

          <Button
            component={Link}
            to={`/gear/${item.sku}`}
            variant="outlined"
            fullWidth
          >
            View Details
          </Button>

          <Button
            variant="contained"
            fullWidth
            onClick={handleAddToBasket}
            disabled={alreadyAdded || item.can_be_rented === false}
          >
            {item.can_be_rented === false
              ? "Display Only"
              : alreadyAdded
                ? "Already in Basket"
                : "Add to Basket"}
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}

export default GearCard;
