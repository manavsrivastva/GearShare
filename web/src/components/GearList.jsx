import { Grid, Typography } from "@mui/material";
import GearCard from "./GearCard";

function GearList({ items }) {
  if (items.length === 0) {
    return (
      <Typography color="text.secondary" sx={{ mt: 3 }}>
        No equipment found.
      </Typography>
    );
  }

  return (
    <Grid container spacing={3}>
      {items.map((item) => (
        <Grid item xs={12} sm={6} md={4} key={item.sku}>
          <GearCard item={item} />
        </Grid>
      ))}
    </Grid>
  );
}

export default GearList;
