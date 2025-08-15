import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from database import *
from dotenv import load_dotenv

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Load environment variables
        load_dotenv()
        
        # Initialize database
        create_tables()
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook.Tab', padding=[20, 5])
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabel', padding=5)
        
        # Create main container
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_add_expense_tab()
        self.create_view_expenses_tab()
        self.create_reports_tab()
        
        # Initialize variables
        self.current_year = datetime.datetime.now().year
        self.current_month = datetime.datetime.now().month
        
        # Load initial data
        self.load_expenses()
    
    def create_add_expense_tab(self):
        """Create the 'Add Expense' tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Add Expense")
        
        # Main frame
        frame = ttk.LabelFrame(tab, text="Add New Expense", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Form fields
        ttk.Label(frame, text="Amount:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.amount_var = tk.DoubleVar()
        ttk.Entry(frame, textvariable=self.amount_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(frame, textvariable=self.category_var, width=18)
        self.category_combobox['values'] = [
            'Food', 'Transport', 'Shopping', 'Bills', 
            'Entertainment', 'Health', 'Education', 'Other'
        ]
        self.category_combobox.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="Date:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar(value=datetime.date.today().strftime('%Y-%m-%d'))
        self.date_entry = DateEntry(
            frame, 
            textvariable=self.date_var, 
            width=18, 
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.date_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="Description:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.desc_text = tk.Text(frame, width=30, height=4)
        self.desc_text.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        ttk.Button(button_frame, text="Add Expense", command=self.add_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)
    
    def create_view_expenses_tab(self):
        """Create the 'View Expenses' tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="View Expenses")
        
        # Filter frame
        filter_frame = ttk.LabelFrame(tab, text="Filter Expenses", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Month:").pack(side=tk.LEFT, padx=5)
        self.month_var = tk.StringVar(value=datetime.datetime.now().strftime('%B'))
        months = ["January", "February", "March", "April", "May", "June", 
                 "July", "August", "September", "October", "November", "December"]
        self.month_combobox = ttk.Combobox(
            filter_frame, 
            textvariable=self.month_var, 
            values=months,
            state='readonly',
            width=12
        )
        self.month_combobox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Year:").pack(side=tk.LEFT, padx=5)
        self.year_var = tk.StringVar(value=str(datetime.datetime.now().year))
        self.year_spinbox = ttk.Spinbox(
            filter_frame, 
            from_=2000, 
            to=2100, 
            textvariable=self.year_var, 
            width=8
        )
        self.year_spinbox.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            filter_frame, 
            text="Filter", 
            command=self.load_expenses
        ).pack(side=tk.LEFT, padx=10)
        
        # Treeview for expenses
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create treeview
        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode='extended',
            columns=('id', 'date', 'category', 'amount', 'description')
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Define columns
        self.tree.column('#0', width=0, stretch=tk.NO)  # Hidden ID column
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('date', width=100, anchor=tk.CENTER)
        self.tree.column('category', width=120, anchor=tk.W)
        self.tree.column('amount', width=100, anchor=tk.E)
        self.tree.column('description', width=300, anchor=tk.W)
        
        # Create headings
        self.tree.heading('id', text='ID', anchor=tk.CENTER)
        self.tree.heading('date', text='Date', anchor=tk.CENTER)
        self.tree.heading('category', text='Category', anchor=tk.CENTER)
        self.tree.heading('amount', text='Amount', anchor=tk.CENTER)
        self.tree.heading('description', text='Description', anchor=tk.CENTER)
        
        # Add context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_expense)
        self.context_menu.add_command(label="Delete", command=self.delete_expense)
        
        # Bind right-click event
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Summary frame
        summary_frame = ttk.Frame(tab)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(summary_frame, text="Total Expenses:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        self.total_var = tk.StringVar(value="$0.00")
        ttk.Label(summary_frame, textvariable=self.total_var, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    
    def create_reports_tab(self):
        """Create the 'Reports' tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")
        
        # Filter frame
        filter_frame = ttk.LabelFrame(tab, text="Report Options", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Month:").pack(side=tk.LEFT, padx=5)
        self.report_month_var = tk.StringVar(value=datetime.datetime.now().strftime('%B'))
        months = ["January", "February", "March", "April", "May", "June", 
                 "July", "August", "September", "October", "November", "December"]
        self.report_month_combobox = ttk.Combobox(
            filter_frame, 
            textvariable=self.report_month_var, 
            values=months,
            state='readonly',
            width=12
        )
        self.report_month_combobox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Year:").pack(side=tk.LEFT, padx=5)
        self.report_year_var = tk.StringVar(value=str(datetime.datetime.now().year))
        self.report_year_spinbox = ttk.Spinbox(
            filter_frame, 
            from_=2000, 
            to=2100, 
            textvariable=self.report_year_var, 
            width=8
        )
        self.report_year_spinbox.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            filter_frame, 
            text="Generate Report", 
            command=self.generate_report
        ).pack(side=tk.LEFT, padx=10)
        
        # Chart frame
        self.chart_frame = ttk.Frame(tab)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def add_expense(self):
        """Add a new expense to the database."""
        try:
            amount = self.amount_var.get()
            category = self.category_var.get()
            date_str = self.date_var.get()
            description = self.desc_text.get('1.0', tk.END).strip()
            
            if not amount or amount <= 0:
                messagebox.showerror("Error", "Please enter a valid amount.")
                return
                
            if not category:
                messagebox.showerror("Error", "Please select a category.")
                return
            
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                return
            
            # Add to database
            transaction_id = add_transaction(amount, category, date, description or None)
            
            if transaction_id:
                messagebox.showinfo("Success", "Expense added successfully!")
                self.clear_form()
                self.load_expenses()
            else:
                messagebox.showerror("Error", "Failed to add expense to database.")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_form(self):
        """Clear the add expense form."""
        self.amount_var.set(0.0)
        self.category_var.set('')
        self.date_var.set(datetime.date.today().strftime('%Y-%m-%d'))
        self.desc_text.delete('1.0', tk.END)
    
    def load_expenses(self):
        """Load expenses for the selected month and year."""
        try:
            month_name = self.month_var.get()
            year = int(self.year_var.get())
            month = datetime.datetime.strptime(month_name, '%B').month
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get expenses from database
            expenses = get_monthly_expenses(year, month)
            
            if not expenses:
                return
            
            # Add expenses to treeview
            total = 0
            for expense in expenses:
                self.tree.insert(
                    '', 'end', 
                    values=(
                        expense['id'],
                        expense['date'].strftime('%Y-%m-%d'),
                        expense['category'],
                        f"${expense['amount']:.2f}",
                        expense.get('description', '')
                    )
                )
                total += float(expense['amount'])
            
            # Update total
            self.total_var.set(f"${total:.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expenses: {str(e)}")
    
    def show_context_menu(self, event):
        """Show context menu on right-click."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def edit_expense(self):
        """Edit selected expense."""
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0], 'values')
        if not item:
            return
            
        # Create edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Expense")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variables
        amount_var = tk.DoubleVar(value=float(item[3].replace('$', '')))
        category_var = tk.StringVar(value=item[2])
        date_var = tk.StringVar(value=item[1])
        
        # Form
        ttk.Label(dialog, text="Amount:").pack(pady=5)
        ttk.Entry(dialog, textvariable=amount_var).pack(pady=5, padx=10, fill=tk.X)
        
        ttk.Label(dialog, text="Category:").pack(pady=5)
        category_combobox = ttk.Combobox(dialog, textvariable=category_var)
        category_combobox['values'] = [
            'Food', 'Transport', 'Shopping', 'Bills', 
            'Entertainment', 'Health', 'Education', 'Other'
        ]
        category_combobox.pack(pady=5, padx=10, fill=tk.X)
        
        ttk.Label(dialog, text="Date (YYYY-MM-DD):").pack(pady=5)
        ttk.Entry(dialog, textvariable=date_var).pack(pady=5, padx=10, fill=tk.X)
        
        ttk.Label(dialog, text="Description:").pack(pady=5)
        desc_text = tk.Text(dialog, height=4)
        desc_text.pack(pady=5, padx=10, fill=tk.X)
        if len(item) > 4:
            desc_text.insert('1.0', item[4])
        
        def save_changes():
            try:
                # Get values
                amount = amount_var.get()
                category = category_var.get()
                date_str = date_var.get()
                description = desc_text.get('1.0', tk.END).strip()
                
                # Validate
                if not amount or amount <= 0:
                    messagebox.showerror("Error", "Please enter a valid amount.")
                    return
                    
                if not category:
                    messagebox.showerror("Error", "Please select a category.")
                    return
                
                try:
                    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                    return
                
                # Update in database
                connection = create_connection()
                if connection:
                    try:
                        cursor = connection.cursor()
                        query = """
                            UPDATE transactions 
                            SET amount = %s, category = %s, date = %s, description = %s
                            WHERE id = %s
                        """
                        cursor.execute(query, (amount, category, date, description or None, item[0]))
                        connection.commit()
                        messagebox.showinfo("Success", "Expense updated successfully!")
                        dialog.destroy()
                        self.load_expenses()
                    except Error as e:
                        messagebox.showerror("Error", f"Failed to update expense: {str(e)}")
                    finally:
                        cursor.close()
                        connection.close()
                
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_expense(self):
        """Delete selected expense."""
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0], 'values')
        if not item:
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
            try:
                connection = create_connection()
                if connection:
                    try:
                        cursor = connection.cursor()
                        cursor.execute("DELETE FROM transactions WHERE id = %s", (item[0],))
                        connection.commit()
                        messagebox.showinfo("Success", "Expense deleted successfully!")
                        self.load_expenses()
                    except Error as e:
                        messagebox.showerror("Error", f"Failed to delete expense: {str(e)}")
                    finally:
                        cursor.close()
                        connection.close()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def generate_report(self):
        """Generate and display expense report."""
        try:
            month_name = self.report_month_var.get()
            year = int(self.report_year_var.get())
            month = datetime.datetime.strptime(month_name, '%B').month
            
            # Clear previous chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # Get expenses by category
            expenses = get_expenses_by_category(year, month)
            
            if not expenses:
                messagebox.showinfo("No Data", f"No expenses found for {month_name} {year}")
                return
            
            # Prepare data
            categories = [expense['category'] for expense in expenses]
            amounts = [float(expense['total']) for expense in expenses]
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Pie chart
            ax1.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
            ax1.set_title(f'Expense Distribution - {month_name} {year}')
            
            # Bar chart
            ax2.bar(categories, amounts, color='skyblue')
            ax2.set_title(f'Expenses by Category - {month_name} {year}')
            ax2.set_ylabel('Amount ($)')
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Adjust layout
            plt.tight_layout()
            
            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

def main():
    """Main function to run the application."""
    try:
        root = tk.Tk()
        app = ExpenseTrackerApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        raise

if __name__ == "__main__":
    main()
