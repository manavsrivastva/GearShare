import { Chip } from "@mui/material";

function AvailabilityBadge({ available }) {
  return (
    <Chip
      label={available > 0 ? `${available} Available` : "Unavailable"}
      color={available > 0 ? "success" : "error"}
      size="small"
    />
  );
}

export default AvailabilityBadge;
