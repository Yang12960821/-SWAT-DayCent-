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
    public partial class Form23 : Form
    {
        public Form23()
        {
            InitializeComponent();
        }

        public Form23(string strTextBox1Text)
        {
            InitializeComponent();
            this.textBox1.Text = strTextBox1Text;
            this.textBox2.Text = strTextBox1Text;
            this.textBox3.Text = strTextBox1Text;
        }

        private void button1_Click(object sender, EventArgs e)
        {

            if (textBox1.Text.Contains("\\"))
            {
                textBox1.Text = textBox1.Text.Replace("\\", "/");
            }

            if (textBox2.Text.Contains("\\"))
            {
                textBox2.Text = textBox2.Text.Replace("\\", "/");
            }

            if (textBox3.Text.Contains("\\"))
            {
                textBox3.Text = textBox3.Text.Replace("\\", "/");
            }

            Form1 lForm1 = (Form1)this.Owner;//把Form2的父窗口指针赋给lForm1
            lForm1.Stroutdir = textBox3.Text;
            lForm1.StrValue = textBox1.Text + " " + textBox2.Text + " " + textBox3.Text;//使用父窗口指针赋值
            this.Close();
        }
    }
}
