import React from 'react';
import { Typography, Table, TableBody, TableCell, TableRow, TableHead, TableContainer } from '@mui/material';

function NutritionResult({ result }) {
  if (!result) return null;

  // Destructure the result object to get food_items and total_calories.
  const { food_items, total_calories } = result;

  return (
    <div>
      <Typography variant="h5" className="results-title">
        Nutrition Data
      </Typography>
      
      {food_items && food_items.length > 0 ? (
        <TableContainer className="nutrition-table">
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Portion (g)</TableCell>
                <TableCell>Calories</TableCell>
                <TableCell>Protein (g)</TableCell>
                <TableCell>Carbs (g)</TableCell>
                <TableCell>Fats (g)</TableCell>
              </TableRow>
            </TableHead>
            
            <TableBody>
              {food_items.map((item, index) => (
                <TableRow key={index}>
                  <TableCell className="food-item-name">{item.name}</TableCell>
                  <TableCell>{item.portion_g}</TableCell>
                  <TableCell>{item.calories}</TableCell>
                  <TableCell>{item.protein_g}</TableCell>
                  <TableCell>{item.carbs_g}</TableCell>
                  <TableCell>{item.fats_g}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Typography variant="body1" className="no-results">
          No food items found.
        </Typography>
      )}
      
      {total_calories !== undefined && (
        <Typography variant="body1" className="total-calories">
          Total Calories: <strong>{total_calories}</strong>
        </Typography>
      )}
    </div>
  );
}

export default NutritionResult;