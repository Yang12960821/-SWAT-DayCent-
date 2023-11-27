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
    public partial class Form3 : Form
    {
        public Form3()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            string text = "";
            if (checkBox1.Checked)
            {
                text += "cproda,";
            }
            if (checkBox2.Checked)
            {
                text += "aglivc,";
            }
            if (checkBox3.Checked)
            {
                text += "drain,";
            }
            if (checkBox4.Checked)
            {
                text += "cgrain,";
            }
            if (checkBox5.Checked)
            {
                text += "bglivc,";
            }
            if (checkBox6.Checked)
            {
                text += "frstc,";
            }
            if (checkBox7.Checked)
            {
                text += "somsc,";
            }
            if (checkBox8.Checked)
            {
                text += "somtc,";
            }
            if (checkBox9.Checked)
            {
                text += "woodc,";
            }
            if (checkBox10.Checked)
            {
                text += "fsysc,";
            }
            if (checkBox11.Checked)
            {
                text += "totsysc,";
            }
            if (checkBox12.Checked)
            {
                text += "npptot,";
            }
            if (checkBox13.Checked)
            {
                text += "nee,";
            }
            if (checkBox14.Checked)
            {
                text += "annet,";
            }
            if (checkBox15.Checked)
            {
                text += "hi,";
            }
            if (checkBox16.Checked)
            {
                text += "agcprd";
            }
            Form1 lForm1 = (Form1)this.Owner;//把Form2的父窗口指针赋给lForm1
            //lForm1.Stroutdir = textBox3.Text;
            if (text.Length != 0)
            {
                text = text.Remove(text.Length - 1, 1);
            }

            lForm1.StrValue = text;//使用父窗口指针赋值
            this.Close();
        }
    }
}
