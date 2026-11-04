
import { createContext, useContext, useReducer } from "react";

const BasketContext = createContext(null);

const initialState = {
  items: [],
};

function basketReducer(state, action) {
  switch (action.type) {
    case "ADD_ITEM": {
      const alreadyExists = state.items.some(
        (item) => item.sku === action.payload.sku
      );

      if (alreadyExists) {
        return state;
      }

      return {
        ...state,
        items: [...state.items, action.payload],
      };
    }

    case "REMOVE_ITEM":
      return {
        ...state,
        items: state.items.filter(
          (item) => item.sku !== action.payload
        ),
      };

    case "CLEAR_BASKET":
      return initialState;

    default:
      return state;
  }
}

export function BasketProvider({ children }) {
  const [state, dispatch] = useReducer(basketReducer, initialState);

  const addItem = (item) => {
    dispatch({ type: "ADD_ITEM", payload: item });
  };

  const removeItem = (sku) => {
    dispatch({ type: "REMOVE_ITEM", payload: sku });
  };

  const clearBasket = () => {
    dispatch({ type: "CLEAR_BASKET" });
  };

  const basketCount = state.items.length;

  const totalReplacementValue = state.items.reduce(
    (total, item) => total + Number(item.price || 0),
    0
  );

  return (
    <BasketContext.Provider
      value={{
        items: state.items,
        addItem,
        removeItem,
        clearBasket,
        basketCount,
        totalReplacementValue,
      }}
    >
      {children}
    </BasketContext.Provider>
  );
}

export function useBasket() {
  const context = useContext(BasketContext);

  if (!context) {
    throw new Error("useBasket must be used inside BasketProvider");
  }

  return context;
}
