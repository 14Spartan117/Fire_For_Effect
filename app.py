# Matplotlib Plot
                fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
                time_axis = np.linspace(current_age, age_at_retire, sim_results.shape[1])
                
                p10 = np.percentile(sim_results, 10, axis=0)
                p50 = np.percentile(sim_results, 50, axis=0)
                p90 = np.percentile(sim_results, 90, axis=0)
                success_rate = np.mean(sim_results[:, -1] >= total_nest_egg_needed) * 100

                # ---------------------------------------------------------
                # NEW: Plot 10 individual simulation paths to show volatility
                # ---------------------------------------------------------
                for i in range(10):
                    # Only label the first one so the legend doesn't duplicate 10 times
                    label = "Individual Market Paths" if i == 0 else ""
                    ax.plot(time_axis, sim_results[i], color='gray', lw=0.75, alpha=0.35, label=label)

                # The Fan Chart (Percentiles)
                ax.fill_between(time_axis, p10, p90, color='teal', alpha=0.2, label='10th - 90th Percentile')
                ax.plot(time_axis, p50, color='teal', lw=3, label='Median Projection')
                
                # The Target Dash
                ax.axhline(y=total_nest_egg_needed, color='red', linestyle='--', lw=2.5, label=f'Target: ${total_nest_egg_needed:,.0f}')

                # Formatting
                ax.set_title(f'Probability of Success: {success_rate:.1f}% (Projected 2026 Dollars)', fontsize=14)
                ax.set_ylabel('Portfolio Value ($)', fontsize=12)
                ax.set_xlabel('Age', fontsize=12)
                ax.legend(loc='upper left')
                ax.grid(True, linestyle='--', alpha=0.5)
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

                st.pyplot(fig)
