import pandas as pd

class Credit:
    MAX_DURATION_YEARS = 30

    def __init__(
            self, credit_amount, interest_nominal, monthly_payment,
            extra_payment_fraction = 0, subsidy_fraction = 0,
            max_repayment_rate = None
            ):
        self.credit_amount = credit_amount
        self.interest_nominal = interest_nominal
        self.monthly_payment = monthly_payment
        self.extra_payment_fraction = extra_payment_fraction
        self.extra_payment = extra_payment_fraction * credit_amount
        self.subsidy_fraction = subsidy_fraction
        if max_repayment_rate is None:
            self.max_repayment = None
        else:
            self.max_repayment = credit_amount * max_repayment_rate / 12

        # calculate initial repayment rate
        initial_interest_payment = self.credit_amount * self.interest_nominal/12
        initial_repayment = self.monthly_payment - initial_interest_payment
        self.initial_repayment_rate = 12 * initial_repayment / self.credit_amount

        self.simulate_credit()

    def simulate_credit(self, startup_duration_months = 0):
        current_debt = self.credit_amount
        current_paid_interest = 0
        current_paid_debt = 0
        interest_this_year = 0
        subsidy_total = 0
        
        # 0th month
        records = [{
            "time": 0,
            "debt": current_debt,
            "paid interest": current_paid_interest,
            "paid debt": current_paid_debt,
            "subsidy": subsidy_total
        }]

        # Next months
        for i in range(1, self.MAX_DURATION_YEARS*12+1):
            interest_payment = current_debt * self.interest_nominal/12
            interest_this_year += interest_payment

            if i <= startup_duration_months:
                # No repayment in the startup period
                repayment = 0
                extra_payment = 0
            else:
                repayment = self.monthly_payment - interest_payment
                
                if self.max_repayment is not None:
                    repayment = min(repayment, self.max_repayment)
                
                # extra payment
                if i%12 == 0:
                    extra_payment = self.extra_payment
                else:
                    extra_payment = 0

                # Don't pay more than the remaining debt
                repayment = min(repayment, current_debt)
                extra_payment = min(extra_payment, current_debt - repayment)


            # subsidy
            if i%12 == 0:
                # calculate subsidy according to
                # interest_this_year * 2 / interest_rate[%]
                # capped to 2500€
                subsidy_new = self.subsidy_fraction\
                    * interest_this_year * 2 / (self.interest_nominal/1e-2)
                subsidy_new = min(subsidy_new, 2950)
                subsidy_total += subsidy_new
                interest_lead = interest_this_year / (current_debt + interest_this_year)
                subsidized_interest_lead = (interest_this_year - subsidy_new)\
                    / (current_debt + interest_this_year)
                print(f"Year={i//12}, Interest this year={interest_this_year}, subsidy_new={subsidy_new}")
                print(f"interest_lead={interest_lead/1e-2:.2f}, subsidized_interest_lead={subsidized_interest_lead/1e-2:.2f}")
                interest_this_year = 0
            
            current_debt -= repayment
            current_paid_interest += interest_payment
            current_paid_debt += repayment

            records.append({
                "time": i,
                "debt": current_debt,
                "paid interest": current_paid_interest,
                "paid debt": current_paid_debt,
                "subsidy": subsidy_total,
                "repayment": repayment,
                "extra_payment": extra_payment,
                "interest_payment": interest_payment,
                "monthly_payment": repayment + interest_payment + extra_payment
            })
            if current_debt == 0:
                break
        
        self.payment_plan = pd.DataFrame.from_records(records)
        self.residual_debt = current_debt
        self.duration = i / 12
        self.interest_total = current_paid_interest
        self.subsidy_total = subsidy_total