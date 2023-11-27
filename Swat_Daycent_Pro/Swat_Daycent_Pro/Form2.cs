using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Swat_Daycent_Pro
{
    public partial class Form2 : Form
    {
        public Form2()
        {
            InitializeComponent(); 
        }

        public Form2(string strTextBox1Text)
        {
            InitializeComponent();
           // this.textBox7.Text = strTextBox1Text;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            string text = "";
            if (checkBox1.Checked)
            {
                text += "PCP/mm,";
            }
            if (checkBox2.Checked)
            {
                text += "PET/mm,";
            }
            if (checkBox3.Checked)
            {
                text += "ET/mm,";
            }
            if (checkBox4.Checked)
            {
                text += "SW_INIT/mm,";
            }
            if (checkBox5.Checked)
            {
                text += "SNOFALL/mm,";
            }
            if (checkBox6.Checked)
            {
                text += "SNOMELT/mm,";
            }
            if (checkBox7.Checked)
            {
                text += "IRR/mm,";
            }
            if (checkBox8.Checked)
            {
                text += "SW_END/mm,";
            }
            if (checkBox9.Checked)
            {
                text += "PERC/mm,";
            }
            if (checkBox10.Checked)
            {
                text += "GW_RCHG/mm,";
            }
            if (checkBox11.Checked)
            {
                text += "DA_RCHG/mm,";
            }
            if (checkBox12.Checked)
            {
                text += "REVAP/mm,";
            }
            if (checkBox13.Checked)
            {
                text += "SA_IRR/mm,";
            }
            if (checkBox14.Checked)
            {
                text += "DA_IRR/mm,";
            }
            if (checkBox15.Checked)
            {
                text += "SA_ST/mm,";
            }
            if (checkBox16.Checked)
            {
                text += "DA_ST/mm,";
            }
            if (checkBox17.Checked)
            {
                text += "SURQ_GEN/mm,";
            }
            if (checkBox18.Checked)
            {
                text += "SURQ_CNT/mm,";
            }
            if (checkBox19.Checked)
            {
                text += "TLOSS/mm,";
            }
            if (checkBox20.Checked)
            {
                text += "LATQGEN/mm,";
            }
            Form1 lForm1 = (Form1)this.Owner;//把Form2的父窗口指针赋给lForm1
            //lForm1.Stroutdir = textBox3.Text;
            if (text.Length!=0)
            {
                text = text.Remove(text.Length - 1, 1);
            }
            
            lForm1.StrValue = text;//使用父窗口指针赋值
            this.Close();
        }
    }
}
